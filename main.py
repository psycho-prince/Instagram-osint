#!/usr/bin/env python3
import argparse
import asyncio
import json
import os
from typing import Dict, Any, List

from utils.banner import print_banner
from utils.cookies import load_cookies, check_cookie_health
from utils.scoring import score_confidence, grade_risk

from core.instagram import (
    resolve_user_id,
    fetch_profile_info,
    infer_timeline_consistency,
    check_private_content_exposure,
)
from enrich.usernames import (
    generate_variants,
    check_username_presence,
    check_username_presence_advanced,
)
from enrich.twitter import twitter_deep_osint
from enrich.leaks import check_leak_signals
from enrich.dorks import generate_dorks
from reports.render import save_reports


VERSION = "1.2.0"  # Version updated for new feature


def build_report_base(username: str) -> Dict[str, Any]:
    return {
        "username": username,
        "user_id": "",
        "username_history": [username],
        "username_changed": True,   # first run establishes baseline
        "avatar_history": [],
        "avatar_changed": True,     # first run establishes baseline
        "full_name": "",
        "biography": "",
        "external_url": "",
        "followers": 0,
        "following": 0,
        "posts": 0,
        "verified": False,
        "business": False,
        "private": False,
        "public_email": "",
        "public_phone": "",
        "profile_pic": "",
        "username_variants": [],
        "platforms": {},
        "advanced_platforms": {},  # New section for advanced checks
        "twitter": {},
        "emails": [],
        "leak_signals": [],
        "timeline_consistency": "unknown",
        "vulnerability_checks": {},
        "confidence": 0.0,
        "risk": "",
        "risk_explanation": "",
        "search_dorks": {},
        "match_level": "NONE",
        "match_reasons": [],
    }


def build_report_base(username: str) -> Dict[str, Any]:
    return {
        "username": username,
        "user_id": "",
        "username_history": [username],
        "username_changed": True,   # first run establishes baseline
        "avatar_history": [],
        "avatar_changed": True,     # first run establishes baseline
        "full_name": "",
        "biography": "",
        "external_url": "",
        "followers": 0,
        "following": 0,
        "posts": 0,
        "verified": False,
        "business": False,
        "private": False,
        "public_email": "",
        "public_phone": "",
        "profile_pic": "",
        "username_variants": [],
        "platforms": {},
        "advanced_platforms": {},  # New section for advanced checks
        "twitter": {},
        "emails": [],
        "leak_signals": {
            "bing_signals": [],
            "pastebin_leaks": [],
        }, # Updated to be a dictionary
        "timeline_consistency": "unknown",
        "vulnerability_checks": {},
        "confidence": 0.0,
        "risk": "",
        "risk_explanation": "",
        "search_dorks": {},
        "match_level": "NONE",
        "match_reasons": [],
    }


async def investigate_username(
    username: str,
    cookies: Dict[str, str],
    debug: bool = False,
) -> Dict[str, Any]:
    report = build_report_base(username)

    if debug:
        print(f"[+] Investigating: {username}")

    # 1️⃣ Resolve Instagram user ID
    uid = await resolve_user_id(username, cookies, debug=debug)
    if not uid:
        raise RuntimeError("Failed to resolve Instagram user ID")

    report["user_id"] = uid
    if debug:
        print(f"[+] User ID resolved: {uid}")

    # 2️⃣ Check for vulnerabilities (UNAUTHENTICATED)
    if debug:
        print("[+] Checking for private content exposure bugs…")
    vuln_results = await check_private_content_exposure(
        report["user_id"], report["username"], debug=debug
    )
    report["vulnerability_checks"]["private_content_exposure"] = vuln_results

    # 3️⃣ Fetch Instagram profile info
    info = await fetch_profile_info(uid, cookies, debug=debug)
    report.update({
        "full_name": info.get("full_name", ""),
        "biography": info.get("biography", ""),
        "external_url": info.get("external_url", "") or "",
        "followers": info.get("followers", 0),
        "following": info.get("following", 0),
        "posts": info.get("posts", 0),
        "verified": info.get("verified", False),
        "business": info.get("business", False),
        "private": info.get("private", False),
        "public_email": info.get("public_email", ""),
        "public_phone": info.get("public_phone", ""),
        "profile_pic": info.get("profile_pic", ""),
    })

    # avatar baseline
    if report["profile_pic"]:
        report["avatar_history"].append({
            "hash": info.get("profile_pic_hash", ""),
            "url": report["profile_pic"],
        })

    # 4️⃣ Username variants + cross-platform presence (Basic)
    report["username_variants"] = generate_variants(username)
    if debug:
        print("[+] Checking cross-platform username presence (basic)…")
    report["platforms"] = await check_username_presence(username, debug=debug)

    # 5️⃣ Advanced cross-platform presence check (with content analysis)
    if debug:
        print("[+] Checking cross-platform username presence (advanced)…")
    report["advanced_platforms"] = await check_username_presence_advanced(
        username, report["full_name"], debug=debug
    )

    # 6️⃣ Twitter/X deep OSINT (if present)
    if report["platforms"].get("twitter", {}).get("exists"):
        if debug:
            print("[+] Twitter/X deep OSINT…")
        report["twitter"] = await twitter_deep_osint(username, debug=debug)
        report["emails"].extend(report["twitter"].get("emails", []))

    # 7️⃣ Leak signals (mentions only, no scraping)
    if debug:
        print("[+] Checking leak signals (Bing & Pastebin)…") # Updated print statement
    leaks_data = await check_leak_signals(username, debug=debug)
    report["leak_signals"] = leaks_data # Assign the dictionary directly

    # 8️⃣ Timeline consistency (cross-platform)
    report["timeline_consistency"] = infer_timeline_consistency(report)

    # 9️⃣ Automated search-engine dorks
    report["search_dorks"] = generate_dorks(report)

    # 🔟 Confidence + risk grading
    report["confidence"] = score_confidence(report)
    report["risk"], report["risk_explanation"] = grade_risk(report)

    return report


async def main():
    parser = argparse.ArgumentParser(
        prog=f"yesitsme v{VERSION}",
        description="Instagram OSINT with enrichment & automated bug detection"
    )
    parser.add_argument("-u", "--username", required=True, help="Target Instagram username")
    parser.add_argument("--cookie", help="Raw cookie string")
    parser.add_argument("--cookies-file", help="Path to cookies.json")
    parser.add_argument("--json", dest="json_out", help="Write JSON report to file")
    parser.add_argument("--md", dest="md_out", help="Write Markdown report to file")
    parser.add_argument("--debug", action="store_true", help="Debug output")
    parser.add_argument("--quiet", action="store_true", help="Suppress banner")

    args = parser.parse_args()

    if not args.quiet:
        print_banner(VERSION)

    # Load cookies
    cookies = load_cookies(args.cookie, args.cookies_file)
    if not cookies:
        raise SystemExit("Cookie required (--cookie or --cookies-file)")

    # Cookie health check
    if args.debug:
        print("[+] Checking cookie health…")
    ok = await check_cookie_health(cookies, debug=args.debug)
    if not ok:
        raise SystemExit("Cookie health check failed")

    # Investigate
    report = await investigate_username(
        args.username,
        cookies,
        debug=args.debug
    )
    
    # Create a simple vulnerability status for the summary
    vuln_summary = "NOT_VULNERABLE"
    if report["vulnerability_checks"]["private_content_exposure"]["legacy_json_vulnerable"] or \
       report["vulnerability_checks"]["private_content_exposure"]["graphql_vulnerable"]:
        vuln_summary = "VULNERABLE"


    # Print summary
    print("\n[+] OSINT RESULT SUMMARY")
    for k in [
        "username", "user_id", "full_name", "biography", "external_url",
        "followers", "following", "posts", "verified", "business", "private",
    ]:
        print(f"{k:<22}: {report.get(k)}")
    
    print(f"{'vulnerability_status':<22}: {vuln_summary}")

    # Print advanced platform results
    print("\n[+] ADVANCED PLATFORM CHECK")
    for platform, result in report.get("advanced_platforms", {}).items():
        if result.get("exists"):
            print(f"  - {platform.upper()} FOUND: {result.get('url')}")
            print(f"    Confidence: {result.get('confidence', 0.0)}")
            if result.get("extracted_full_name"):
                print(f"    Full Name: {result.get('extracted_full_name')}")
            if result.get("extracted_bio"):
                print(f"    Bio: {result.get('extracted_bio', '')[:100]}...")
            if result.get('matches'):
                print(f"    Matches: {', '.join(result.get('matches', []))}")
        else:
            print(f"  - {platform.upper()} NOT FOUND (Status: {result.get('status', 'N/A')})")

    # Print Pastebin leaks
    pastebin_leaks = report["leak_signals"].get("pastebin_leaks", [])
    if pastebin_leaks:
        print("\n[+] PASTEBIN LEAKS FOUND")
        for leak in pastebin_leaks:
            print(f"  - URL: {leak['url']}")
            print(f"    Found Username: {leak['found_username']}")
            print(f"    Found Keywords: {', '.join(leak['found_keywords'])}")
            print(f"    Snippet: {leak['snippet'][:150]}...")
    else:
        print("\n[+] NO PASTEBIN LEAKS FOUND")


    print("\n[+] ANALYSIS")
    for k in ["timeline_consistency", "confidence", "risk", "risk_explanation"]:
         print(f"{k:<22}: {report.get(k)}")

    # Save reports
    if args.json_out or args.md_out:
        save_reports(report, args.json_out, args.md_out)
        print("\n[+] Reports saved:")
        if args.json_out:
            print(f"    JSON → {args.json_out}")
        if args.md_out:
            print(f"    MD   → {args.md_out}")


if __name__ == "__main__":
    asyncio.run(main())
