# Portable adaptation. Optional paid route, off by default. Historical model IDs/prices
# require current provider verification before --allow-paid. No account/key is included.
#!/usr/bin/env python3
"""Optional paid Kie image adapter for hand-drawn-style.

Native current-runtime image generation remains the default. Use this adapter only
when the user explicitly authorizes Kie for the request. Default paid model is
ChatGPT Images 2.5 Flare; official references automatically select image-to-image.

Example after authorization:
    python3 generate_hand_drawn.py --allow-paid --prompt-file prompt.txt --output out.png
    python3 generate_hand_drawn.py --allow-paid --prompt-file prompt.txt --reference-url https://example.com/official-logo.png --output out.png

Public Kie schema verified 2026-09-10; no paid generation test performed.
"""

import argparse
import base64
import json
import os
import re
import sys
import time
import uuid
import urllib.request
import urllib.error
from pathlib import Path


# --- Configuration ---

VALID_ASPECT_RATIOS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4", "4:1",
    "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9", "27:16", "16:27", "9:8", "8:9", "auto",
]

VALID_RESOLUTIONS = ["1K", "2K", "4K"]

DEFAULT_MODEL = "gpt-image-2-5-flare-text-to-image"
DEFAULT_RESOLUTION = "4K"
DEFAULT_ASPECT_RATIO = "1:1"
DEFAULT_OUTPUT_FORMAT = "png"

KIE_API_BASE = "https://api.kie.ai/api/v1/jobs"
KIE_CREATE_TASK_URL = f"{KIE_API_BASE}/createTask"
KIE_TASK_STATUS_URL = f"{KIE_API_BASE}/recordInfo"

SUPPORTED_LOGO_FORMATS = {".jpg", ".jpeg", ".png", ".webp"}

MIME_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}

POLL_INITIAL_INTERVAL = 3
POLL_MAX_INTERVAL = 8
POLL_TIMEOUT = 600

SCRIPT_DIR = Path(__file__).parent

DEFAULT_REGISTRY_PATH = SCRIPT_DIR / "logo_registry.json"
DEFAULT_LOGO_DIR = SCRIPT_DIR / "logos"

def load_api_key():
    """Use only the customer-provided environment; never scan private files."""
    return os.environ.get("KIE_API_KEY")


def load_registry(registry_path=None):
    """Load the logo registry JSON. Returns the 'brands' dict or empty dict."""
    path = Path(registry_path) if registry_path else DEFAULT_REGISTRY_PATH
    if not path or not path.exists():
        return {}
    try:
        with open(path) as f:
            data = json.load(f)
        return data.get("brands", {})
    except (json.JSONDecodeError, OSError) as e:
        print(f"WARNING: Could not load registry at {path}: {e}", file=sys.stderr)
        return {}


def detect_brands_in_prompt(prompt, registry):
    """Scan the SCENE section of the prompt for brand keywords.

    The evergreen prompt lists every supported brand in its LOGOS AND BRANDS
    clause, so a naive whole-prompt scan over-matches. Restrict the scan to
    the SCENE block. Fall back to whole-prompt scanning if no SCENE block is
    found.
    """
    scene = re.search(r"SCENE:", prompt, re.IGNORECASE)
    search_text = prompt
    if scene:
        lines = prompt[scene.end():].splitlines(keepends=True)
        headers = {"TEXT", "STYLE LOCK", "COLOR PALETTE", "CHARACTERS",
                   "LOGOS AND BRANDS", "VARIATION", "AVOID", "BRAND EMPHASIS"}
        for index, line in enumerate(lines[1:], 1):
            name, separator, _ = line.lstrip().partition(":")
            if separator and name.upper() in headers:
                search_text = "".join(lines[:index])
                break
    search_text = search_text.lower()

    matched = []
    for brand_key, brand_data in registry.items():
        keywords = brand_data.get("keywords", [brand_key])
        for keyword in keywords:
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, search_text):
                if brand_key not in matched:
                    matched.append(brand_key)
                break

    return matched


def contained_asset_path(directory, filename):
    """Resolve a manifest asset inside its chosen directory, including symlinks."""
    if (not isinstance(filename, str) or not filename
            or any(char in filename for char in ("\\", ":"))
            or any(ord(char) < 32 or 127 <= ord(char) < 160 for char in filename)):
        raise ValueError("Asset filename must be a portable relative path")
    relative = Path(filename)
    if relative.is_absolute() or any(part in {"", ".", ".."} for part in filename.split("/")):
        raise ValueError("Asset filename cannot be absolute or contain traversal components")
    root = Path(directory).resolve()
    candidate = (root / relative).resolve()
    if not candidate.is_relative_to(root):
        raise ValueError("Asset filename escapes its selected directory")
    return candidate


def load_logo_images(brands, registry, logo_dir=None):
    """Load logo image files for the specified brands.

    Returns a list of (brand_name, file_path, mime_type, data_uri) tuples.
    Caps at 2 images per brand to keep payload size reasonable.
    """
    dir_path = Path(logo_dir) if logo_dir else DEFAULT_LOGO_DIR
    loaded = []

    for brand_key in brands:
        brand_data = registry.get(brand_key)
        if not brand_data:
            raise ValueError(f"Required brand reference is absent from the registry: {brand_key}. Add the current official asset before generation.")

        files = brand_data.get("files", [])
        count = 0
        max_per_brand = 2

        for filename in files:
            if count >= max_per_brand:
                break

            filepath = contained_asset_path(dir_path, filename)
            ext = filepath.suffix.lower()

            if ext not in SUPPORTED_LOGO_FORMATS:
                continue

            if not filepath.exists():
                print(f"  WARNING: Logo file missing: {filepath}", file=sys.stderr)
                continue

            mime = MIME_TYPES.get(ext, "image/png")
            image_bytes = filepath.read_bytes()
            b64_data = base64.b64encode(image_bytes).decode("utf-8")
            data_uri = f"data:{mime};base64,{b64_data}"
            loaded.append((brand_key, str(filepath), mime, data_uri))
            count += 1

        if count == 0:
            raise ValueError(f"No readable supported official reference for required brand: {brand_key}. Generation was not submitted.")

    return loaded


def build_logo_instruction(brands, registry):
    """Build a text instruction telling the model to use the reference logos."""
    parts = []
    parts.append('LOGO REFERENCE IMAGES: Use each attached current official logo as a structural reference. Preserve its exact recognizable structure, component count, proportions, spacing, negative space, and wordmark spelling. Render the mark in the SAME image style as the scene, matching its linework, materials, texture, palette treatment, light, depth, and perspective. Integrate each required mark once into a meaningful physical or designed surface during generation. Style-matched drawing and color/material treatment are intentional; invented or distorted logo structure is forbidden. No pristine pasted asset, flat overlay, or unrelated app-icon tile. Use the official reference and match the selected style.')

    for brand_key in brands:
        brand_data = registry.get(brand_key, {})
        desc = brand_data.get("description", "")
        if desc:
            parts.append(f"  - {brand_key.upper()}: {desc}")

    return "\n".join(parts)


def kie_api_request(url, api_key, data=None, method="GET"):
    """Make an authenticated request to the Kie API."""
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    if data is not None:
        body = json.dumps(data).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    else:
        req = urllib.request.Request(url, headers=headers, method=method)

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        error_body = e.read().decode("utf-8", errors="replace")
        print(f"ERROR: Kie API returned HTTP {e.code}", file=sys.stderr)
        print(f"  Response: {error_body[:500]}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"ERROR: Could not reach Kie API: {e.reason}", file=sys.stderr)
        sys.exit(1)


GPT25_MODELS = {
    "gpt-image-2-5-flare-text-to-image": "gpt-image-2-5-flare-image-to-image",
    "gpt-image-2-5-sunburst-text-to-image": "gpt-image-2-5-sunburst-image-to-image",
}
GPT25_RATIOS = {"auto", "1:1", "3:2", "2:3", "4:3", "3:4", "16:9", "9:16", "21:9", "27:16", "16:27", "9:8", "8:9"}
GPT25_1K_ONLY = {"27:16", "16:27", "9:8", "8:9"}


def build_create_payload(model, prompt, image_inputs, aspect_ratio, resolution, output_format):
    """Build a request using the model's verified schema; no network or credentials."""
    if model in GPT25_MODELS or model in GPT25_MODELS.values():
        if not prompt.strip() or len(prompt) > 20000:
            raise ValueError("GPT Images 2.5 requires a nonempty prompt of at most 20,000 characters.")
        if aspect_ratio not in GPT25_RATIOS or resolution not in ("1K", "2K", "4K"):
            raise ValueError("Unsupported GPT Images 2.5 aspect ratio or resolution.")
        if aspect_ratio in GPT25_1K_ONLY and resolution != "1K":
            raise ValueError("This GPT Images 2.5 aspect ratio supports 1K only.")
        if len(image_inputs) > 16:
            raise ValueError("GPT Images 2.5 supports at most 16 reference images.")
        if any(not value.startswith(("https://", "data:image/")) for value in image_inputs):
            raise ValueError("References must be HTTPS URLs or local image data URLs for upload.")
        if image_inputs:
            model = GPT25_MODELS.get(model, model)
        elif model in GPT25_MODELS.values():
            raise ValueError("The image-to-image model requires at least one reference image.")
        fields = {"prompt": prompt, "aspect_ratio": aspect_ratio, "resolution": resolution, "background": "auto"}
        if image_inputs:
            fields["input_urls"] = list(image_inputs)
        return {"model": model, "input": fields}
    if model == "gpt-image-2-text-to-image":
        raise ValueError("The old GPT Image 2 route is retired; use the documented Images 2.5 model.")
    return {"model": model, "input": {"prompt": prompt, "image_input": image_inputs,
            "aspect_ratio": aspect_ratio, "resolution": resolution, "output_format": output_format}}


def upload_reference(api_key, data_url):
    """Upload an authorized local reference before supplying its hosted URL to Kie."""
    extension = "jpg" if data_url.startswith("data:image/jpeg;") else data_url.split(";", 1)[0].rsplit("/", 1)[-1]
    result = kie_api_request("https://kieai.redpandaai.co/api/file-base64-upload", api_key, data={
        "base64Data": data_url, "uploadPath": "images/user-uploads",
        "fileName": f"image-reference-{uuid.uuid4().hex}.{extension}"})
    data = result.get("data") or {}
    url = data.get("downloadUrl") or data.get("fileUrl")
    if result.get("code") != 200 or not isinstance(url, str) or not url.startswith("https://"):
        raise ValueError("Reference upload did not return a valid HTTPS file URL; generation was not submitted.")
    return url


def create_task(api_key, model, prompt, image_inputs, aspect_ratio, resolution, output_format):
    """Submit an explicitly authorized Kie generation with verified model fields."""
    payload = build_create_payload(model, prompt, image_inputs, aspect_ratio, resolution, output_format)
    if "input_urls" in payload["input"]:
        payload["input"]["input_urls"] = [upload_reference(api_key, ref) if ref.startswith("data:") else ref
                                           for ref in payload["input"]["input_urls"]]
    model = payload["model"]

    print(f"  Creating task with Kie API (model: {model})...")
    result = kie_api_request(KIE_CREATE_TASK_URL, api_key, data=payload)

    if result.get("code") != 200:
        print(f"ERROR: Task creation failed: {result.get('msg', 'Unknown error')}", file=sys.stderr)
        sys.exit(1)

    task_id = result.get("data", {}).get("taskId")
    if not task_id:
        task_id = result.get("data", {}).get("task_id") or result.get("taskId")

    if not task_id:
        print(f"ERROR: No task ID in response: {json.dumps(result, indent=2)[:500]}", file=sys.stderr)
        sys.exit(1)

    print(f"  Task created: {task_id}")
    return task_id


def poll_task(api_key, task_id):
    """Poll for task completion. Returns the result URLs."""
    interval = POLL_INITIAL_INTERVAL
    elapsed = 0

    while elapsed < POLL_TIMEOUT:
        time.sleep(interval)
        elapsed += interval

        url = f"{KIE_TASK_STATUS_URL}?taskId={task_id}"
        result = kie_api_request(url, api_key)

        data = result.get("data", {})
        state = data.get("state", "unknown")

        if state == "success":
            result_json_str = data.get("resultJson", "{}")
            try:
                result_json = json.loads(result_json_str) if isinstance(result_json_str, str) else result_json_str
            except json.JSONDecodeError:
                result_json = {}

            urls = result_json.get("resultUrls", [])
            if urls:
                cost_time = data.get("costTime", 0)
                print(f"  Task completed in {cost_time / 1000:.1f}s")
                return urls
            else:
                print(f"ERROR: Task succeeded but no result URLs found.", file=sys.stderr)
                print(f"  Result data: {json.dumps(data, indent=2)[:500]}", file=sys.stderr)
                sys.exit(1)

        elif state == "fail":
            fail_msg = data.get("failMsg", "Unknown failure")
            fail_code = data.get("failCode", "")
            print(f"ERROR: Task failed: {fail_msg} (code: {fail_code})", file=sys.stderr)
            sys.exit(1)

        else:
            progress = data.get("progress", "")
            status_msg = f"  Status: {state}"
            if progress:
                status_msg += f" ({progress}%)"
            status_msg += f" [{elapsed}s elapsed]"
            print(status_msg)

        interval = min(interval + 1, POLL_MAX_INTERVAL)

    print(f"ERROR: Task timed out after {POLL_TIMEOUT}s", file=sys.stderr)
    sys.exit(1)


def download_image(url, output_path):
    """Download the generated image from the result URL."""
    print(f"  Downloading image...")
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Accept": "image/png,image/*,*/*",
            "Referer": "https://api.kie.ai/",
        })
        with urllib.request.urlopen(req, timeout=120) as resp:
            image_data = resp.read()

        os.makedirs(os.path.dirname(os.path.abspath(output_path)) or ".", exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(image_data)

        print(f"\nImage saved to: {output_path}")
        print(f"  Size: {len(image_data):,} bytes")
        return True

    except Exception as e:
        print(f"ERROR: Failed to download image: {e}", file=sys.stderr)
        return False


def generate_image(prompt, output_path, model=None, aspect_ratio=None, resolution=None,
                   output_format=None, brands=None, registry=None,
                   logo_dir=None, no_logos=False, image_inputs_extra=None, reference_urls=None, allow_paid=False):
    """Generate an image using the Kie API with optional logo references."""
    if not allow_paid:
        raise ValueError("Kie is a paid opt-in backup. Use native generation unless this request explicitly authorizes Kie; then pass --allow-paid.")

    api_key = load_api_key()
    if not api_key:
        print("ERROR: KIE_API_KEY not found.", file=sys.stderr)
        print("Set it only as an environment variable:", file=sys.stderr)
        print('  # KIE_API_KEY is loaded only from your own environment.', file=sys.stderr)
        sys.exit(1)

    model = model or DEFAULT_MODEL
    aspect_ratio = aspect_ratio or DEFAULT_ASPECT_RATIO
    res = resolution or DEFAULT_RESOLUTION
    fmt = output_format or DEFAULT_OUTPUT_FORMAT

    if brands and no_logos:
        raise ValueError("Do not combine required brands with --no-logos.")
    if brands and not registry and not reference_urls:
        raise ValueError("Required brands need an official local registry or hosted reference URLs.")

    image_inputs = list(reference_urls or [])
    logo_instruction = ""

    if not no_logos and registry:
        if brands is None:
            brands = detect_brands_in_prompt(prompt, registry)

        if brands:
            print(f"  Detected brands: {', '.join(brands)}")
            logo_images = load_logo_images(brands, registry, logo_dir)
            print(f"  Loaded {len(logo_images)} reference logo images")
            logo_instruction = build_logo_instruction(brands, registry)

            for brand_key, filepath, mime, data_uri in logo_images:
                image_inputs.append(data_uri)
                print(f"  Attached: {brand_key} logo ({Path(filepath).name})")
        else:
            print("  No brand logos detected in prompt (use --brands to specify manually)")

    # Extra image inputs (e.g. an uploaded image to restyle)
    if image_inputs_extra:
        for extra in image_inputs_extra:
            image_inputs.append(extra)
            print(f"  Attached extra image input")

    if logo_instruction:
        full_prompt = f"{logo_instruction}\n\n---\n\n{prompt}"
    else:
        full_prompt = prompt

    print(f"\nGenerating image...")
    print(f"  Model: {model}")
    print(f"  Aspect ratio: {aspect_ratio}")
    print(f"  Resolution: {res}")
    print(f"  Format: {fmt}")
    print(f"  Image inputs: {len(image_inputs)} ({'logos+' if logo_instruction else ''}{'restyle' if image_inputs_extra else ''})")
    print(f"  Output: {output_path}")
    print()

    task_id = create_task(api_key, model, full_prompt, image_inputs, aspect_ratio, res, fmt)
    result_urls = poll_task(api_key, task_id)

    if result_urls:
        success = download_image(result_urls[0], output_path)
        if not success:
            sys.exit(1)
    else:
        print("ERROR: No image URLs returned.", file=sys.stderr)
        sys.exit(1)


def list_brands(registry):
    """Print all available brands and their keywords."""
    if not registry:
        print("No brands in logo registry (or registry file missing).")
        return
    print("Available brands in logo registry:\n")
    for brand_key, brand_data in sorted(registry.items()):
        keywords = ", ".join(brand_data.get("keywords", []))
        desc = brand_data.get("description", "")
        file_count = len(brand_data.get("files", []))
        print(f"  {brand_key}")
        print(f"    Keywords: {keywords}")
        print(f"    Files: {file_count} reference images")
        if desc:
            print(f"    Description: {desc}")
        print()


def encode_local_image_as_data_uri(path):
    """Encode a local image file as a data URI for image_input."""
    p = Path(path)
    ext = p.suffix.lower()
    if ext not in SUPPORTED_LOGO_FORMATS:
        print(f"ERROR: Unsupported image format for restyle: {ext}", file=sys.stderr)
        sys.exit(1)
    if not p.exists():
        print(f"ERROR: Image not found: {path}", file=sys.stderr)
        sys.exit(1)
    mime = MIME_TYPES.get(ext, "image/png")
    image_bytes = p.read_bytes()
    b64 = base64.b64encode(image_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def main():
    parser = argparse.ArgumentParser(
        description="Generate hand-drawn animatic-storyboard images via Kie API"
    )
    parser.add_argument("--prompt", type=str, help="The image generation prompt")
    parser.add_argument("--prompt-file", type=str, help="Path to a text file containing the prompt")
    parser.add_argument(
        "--model", type=str, default=DEFAULT_MODEL,
        help=f"Kie model name (default: {DEFAULT_MODEL}). Images 2.5 references select its matching image-to-image model.",
    )
    parser.add_argument(
        "--aspect-ratio", type=str, default=DEFAULT_ASPECT_RATIO,
        choices=VALID_ASPECT_RATIOS,
        help=f"Image aspect ratio (default: {DEFAULT_ASPECT_RATIO})",
    )
    parser.add_argument(
        "--resolution", type=str, default=DEFAULT_RESOLUTION,
        choices=VALID_RESOLUTIONS,
        help=f"Output resolution (default: {DEFAULT_RESOLUTION})",
    )
    parser.add_argument(
        "--output-format", type=str, default=DEFAULT_OUTPUT_FORMAT,
        choices=["png", "jpg"],
        help=f"Output format (default: {DEFAULT_OUTPUT_FORMAT})",
    )
    parser.add_argument("--output", type=str, required=False, help="Output file path")

    parser.add_argument(
        "--brands", nargs="+", type=str, default=None,
        help="Manually specify brands to include logos for (e.g., --brands claude chatgpt)",
    )
    parser.add_argument(
        "--no-logos", action="store_true",
        help="Skip logo references entirely (required for GPT Image 2)",
    )
    parser.add_argument(
        "--logo-dir", type=str, default=None,
        help=f"Directory containing logo files (default: {DEFAULT_LOGO_DIR})",
    )
    parser.add_argument(
        "--registry", type=str, default=None,
        help=f"Path to logo_registry.json (default: {DEFAULT_REGISTRY_PATH})",
    )
    parser.add_argument(
        "--restyle-image", type=str, default=None,
        help="Path to a local image to restyle with Images 2.5 or an explicitly selected compatible model",
    )
    parser.add_argument(
        "--list-brands", action="store_true",
        help="List all brands in the registry and exit",
    )

    parser.add_argument("--allow-paid", action="store_true", help="Confirm Kie spend was explicitly authorized for this request.")
    parser.add_argument("--reference-url", action="append", default=[], help="HTTPS reference image; repeat for multiple official logos or edit sources.")
    args = parser.parse_args()
    if not args.list_brands and not args.allow_paid:
        parser.error("Native image generation is the default. Use --allow-paid only after explicit Kie authorization.")

    registry = load_registry(args.registry)

    if args.list_brands:
        list_brands(registry)
        return

    if args.prompt_file:
        with open(args.prompt_file) as f:
            prompt = f.read().strip()
    elif args.prompt:
        prompt = args.prompt
    else:
        print("ERROR: Provide either --prompt or --prompt-file", file=sys.stderr)
        sys.exit(1)

    if not args.output:
        print("ERROR: --output is required", file=sys.stderr)
        sys.exit(1)

    image_inputs_extra = None
    if args.restyle_image:
        image_inputs_extra = [encode_local_image_as_data_uri(args.restyle_image)]

    generate_image(
        prompt=prompt,
        output_path=args.output,
        model=args.model,
        aspect_ratio=args.aspect_ratio,
        resolution=args.resolution,
        output_format=args.output_format,
        brands=args.brands,
        registry=registry,
        logo_dir=args.logo_dir,
        no_logos=args.no_logos,
        reference_urls=args.reference_url,
        allow_paid=args.allow_paid,
        image_inputs_extra=image_inputs_extra,
    )


if __name__ == "__main__":
    main()
