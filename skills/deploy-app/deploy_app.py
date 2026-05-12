#!/usr/bin/env python3
"""
Deploy a published Domo custom app to App Studio as a full-page card.

Run after `domo publish` to wrap the resulting design in an App Studio app.

Usage:
  python3 deploy_app.py \
    --design-id <UUID> \
    --title "My App" \
    --instance domo-paul-mccusker.domo.com \
    --token DDCI...

  # With dataset mappings (alias=dataset_id pairs from manifest.json)
  python3 deploy_app.py ... \
    --mapping loans=1165f255-... \
    --mapping alerts=4d8c706c-...
"""
import argparse
import json
import sys
import time
import urllib.parse

import requests


def parse_mappings(pairs):
    """Convert ['alias=uuid', ...] into Domo mapping objects."""
    mappings = []
    for p in pairs or []:
        if "=" not in p:
            print(f"ERROR: bad --mapping {p!r}, expected alias=dataset_id", file=sys.stderr)
            sys.exit(1)
        alias, dsid = p.split("=", 1)
        mappings.append({
            "alias":     alias.strip(),
            "dataSetId": dsid.strip(),
            "fields":    [],
            "dql":       None,
        })
    return mappings


def deploy(instance, token, design_id, title, description, mappings, nav_label, nav_icon):
    base     = f"https://{instance}"
    api_base = f"{base}/api"
    headers  = {"X-DOMO-Developer-Token": token, "Content-Type": "application/json"}

    def api(method, path, **kw):
        r = getattr(requests, method)(f"{api_base}{path}", headers=headers, **kw)
        if not r.ok:
            print(f"  ✗ {method.upper()} {path} → {r.status_code}: {r.text[:400]}",
                  file=sys.stderr)
            r.raise_for_status()
        return r.json() if r.content else {}

    def raw(method, path, **kw):
        r = getattr(requests, method)(f"{base}{path}", headers=headers, **kw)
        if not r.ok:
            print(f"  ✗ {method.upper()} {path} → {r.status_code}: {r.text[:400]}",
                  file=sys.stderr)
            r.raise_for_status()
        return r.json() if r.content else {}

    # 1. Create app
    print(f"→ Creating app {title!r}")
    app_resp    = api("post", "/content/v1/dataapps",
                      json={"title": title, "description": description})
    app_id      = app_resp.get("dataAppId") or app_resp.get("id")
    landing_pid = app_resp.get("landingViewId")
    print(f"  ✓ App   id={app_id}")
    print(f"  ✓ Page  id={landing_pid}")

    # 2. Hide chrome / set LEFT nav
    print("→ Configuring shell (LEFT nav, no chrome)")
    app_full = api("get", f"/content/v1/dataapps/{app_id}?includeHiddenViews=true")
    app_full.update({
        "navOrientation":     "LEFT",
        "showDomoNavigation": False,
        "showNavigation":     True,
        "showTitle":          False,
        "showLogo":           False,
    })
    requests.put(
        f"{api_base}/content/v1/dataapps/{app_id}?includeHiddenViews=true",
        headers=headers, json=app_full,
    ).raise_for_status()

    # 3. Create the pro-code card
    print(f"→ Creating pro-code card for design {design_id}")
    ctx = raw("post", "/domoapps/apps/v2/contexts", json={
        "designId":         design_id,
        "mapping":          mappings,
        "collections":      [],
        "accountMapping":   [],
        "actionMapping":    [],
        "workflowMapping":  [],
        "packageMapping":   [],
        "isDisabled":       False,
    })
    ctx_id = ctx[0]["id"] if isinstance(ctx, list) else ctx["id"]

    raw("post",
        f"/domoapps/apps/v2?fullpage=false&pageId={landing_pid}"
        f"&cardTitle={urllib.parse.quote(title)}",
        json={"contextId": ctx_id, "id": ctx_id})

    time.sleep(2)
    cards = api("get", f"/content/v1/pages/{landing_pid}/cards")
    card_id = next((c["id"] for c in (cards if isinstance(cards, list) else [])
                    if c.get("title") == title), None)
    if not card_id:
        print(f"  ✗ Card not found on page after creation. Check title uniqueness.",
              file=sys.stderr)
        sys.exit(1)
    print(f"  ✓ Card  id={card_id}")

    # 4. Apply full-page layout
    print("→ Applying full-page layout")
    time.sleep(1)
    layout = api("get", f"/content/v4/pages/{landing_pid}/layouts")
    lid = layout["layoutId"]

    ck_map = {c.get("cardId"): c.get("contentKey")
              for c in layout.get("content", []) if c.get("cardId")}
    target_ck = ck_map.get(card_id)
    if target_ck is None:
        print(f"  ✗ Card not in layout content array.", file=sys.stderr)
        sys.exit(1)

    HIDE = {
        "hideTitle":       True,
        "hideDescription": True,
        "hideSummary":     True,
        "hideFooter":      True,
        "hideBorder":      True,
        "hideMargins":     True,
        "hideTimeframe":   True,
        "hideWrench":      True,
        "fitToFrame":      True,
        "acceptFilters":   True,
        "acceptDateFilter":True,
        "style":           {"sourceId": "ca8", "textColor": None},
    }

    new_content = []
    for c in layout.get("content", []):
        item = dict(c)
        if c.get("cardId") == card_id:
            item.update(HIDE)
        new_content.append(item)

    new_template = []
    for t in layout.get("standard", {}).get("template", []):
        item = dict(t)
        if item.get("contentKey") == target_ck:
            item.update({**HIDE,
                         "x": 0, "y": 0, "width": 60, "height": 94,
                         "virtual": False, "virtualAppendix": False})
        new_template.append(item)

    compact = [{
        "contentKey": target_ck, "type": "CARD",
        "x": 0, "y": 0, "width": 12, "height": 8,
        "virtual": False, "virtualAppendix": False, "children": [],
        **HIDE,
    }]

    layout["standard"]["template"] = new_template
    layout["compact"]["template"]  = compact
    layout["content"]              = new_content
    layout["isDynamic"]            = True

    requests.put(f"{api_base}/content/v4/pages/layouts/{lid}/writelock",
                 headers=headers, json={}).raise_for_status()
    r = requests.put(f"{api_base}/content/v4/pages/layouts/{lid}",
                     headers=headers, json=layout)
    requests.delete(f"{api_base}/content/v4/pages/layouts/{lid}/writelock",
                    headers=headers)
    if not r.ok:
        print(f"  ✗ Layout PUT {r.status_code}: {r.text[:300]}", file=sys.stderr)
        sys.exit(1)
    print("  ✓ Layout: full-page")

    # 5. Optional nav label/icon
    if nav_label or nav_icon:
        print("→ Setting navigation label/icon")
        nav = requests.get(f"{api_base}/content/v1/dataapps/{app_id}/navigation",
                           headers=headers).json()
        if isinstance(nav, list):
            for item in nav:
                if (item.get("entity") == "VIEW"
                        and str(item.get("entityId", "")) == str(landing_pid)):
                    if nav_icon:
                        item["icon"] = {"value": nav_icon, "size": "DEFAULT"}
                    if nav_label:
                        item["title"] = nav_label
                    item["visible"] = True
            requests.put(
                f"{api_base}/content/v1/dataapps/{app_id}/navigation/reorder",
                headers=headers, json=nav,
            ).raise_for_status()
            print("  ✓ Navigation updated")

    print()
    print(f"App URL: {base}/app/{app_id}")
    print(f"App ID:  {app_id}")
    print(f"Page ID: {landing_pid}")
    print(f"Card ID: {card_id}")
    return {
        "app_id":  app_id,
        "page_id": landing_pid,
        "card_id": card_id,
        "url":     f"{base}/app/{app_id}",
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--design-id", required=True,
                   help="Design UUID from `domo publish`")
    p.add_argument("--title", required=True,
                   help="App Studio app title (also used as card title)")
    p.add_argument("--description", default="",
                   help="App Studio app description")
    p.add_argument("--instance", required=True,
                   help="e.g. domo-paul-mccusker.domo.com")
    p.add_argument("--token", required=True,
                   help="Domo developer token (DDCI…)")
    p.add_argument("--mapping", action="append", default=[],
                   help="Dataset mapping as alias=dataset_id; pass once per dataset")
    p.add_argument("--nav-label", default=None,
                   help="Override the page's left-nav label")
    p.add_argument("--nav-icon", default=None,
                   help="Domo nav icon name (e.g. 'analytics', 'data-app', 'magic')")
    args = p.parse_args()

    mappings = parse_mappings(args.mapping)
    result = deploy(
        instance=args.instance,
        token=args.token,
        design_id=args.design_id,
        title=args.title,
        description=args.description or args.title,
        mappings=mappings,
        nav_label=args.nav_label,
        nav_icon=args.nav_icon,
    )
    # Also dump JSON for scripts that pipe this
    print()
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
