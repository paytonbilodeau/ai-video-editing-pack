# The AI editing email workflow

This is a reusable version of the free editing-pack funnel. It collects an email, confirms the subscriber, gives access to the pack and starts a 22-lesson guide. It includes the mechanism and editable lesson copy, not subscriber data, account credentials or a live Kit automation export.

## Reader flow

1. A short landing page explains “Edit videos faster and better with AI.” Put the email field and button near the top on desktop and mobile. An optional name field should earn the extra friction.
2. Submission shows a check-your-inbox message. Keep marketing subscription inactive until confirmation; use the email provider's native confirmation mechanism.
3. The personal confirmation email asks the person to confirm. Its button is a real provider confirmation link, not a static GitHub link disguised as confirmation.
4. On confirmation, send the reader to the pack's START HERE page and enter them into the sequence. Lesson 1 has a zero-hour delay; lessons 2–22 have one-day delays with every sending day enabled.
5. Explain that GitHub holds the files and setup guide, and that the first email is also arriving. Beginners can download the ZIP without understanding Git or coding.

## Set it up in Kit

Create your own landing page, incentive/confirmation email, sequence and visual automation. Turn on native double opt-in and disable automatic confirmation. Use the landing-page entry in an active visual automation that adds confirmed subscribers to the sequence. Check current Kit behavior with a new test address: an unconfirmed subscriber must receive zero marketing lessons, then receive lesson 1 after the real confirmation click. Do not approximate this by using a fixed delay.

Set the post-confirmation destination to your pack's setup URL. Set the signup success message to “Check your inbox and confirm your email. The confirmation button opens the setup guide, and your first email follows.” Customize the confirmation copy in [CONFIRMATION.md](CONFIRMATION.md). Use [settings.example.json](settings.example.json) as a checklist, not an API payload. No live account IDs are supplied.

Before launch, authenticate your sending domain using the provider's current instructions. Check the received email's SPF, DKIM and DMARC results, unsubscribe behavior, sender identity and reply address. Double opt-in improves consent and list quality; it cannot guarantee Inbox or Primary placement. Test with your own address and inspect a real received message.

## The 22 lessons

[The sequence map](SEQUENCE.md) links all lesson templates. Customize the instructor name, URLs and first-person examples before importing. Some first-person examples come from the original guide; replace them with experiences and tool choices you can honestly claim. Add a percentage result only if your own test supports it, and identify it as your experience rather than a reader guarantee. The lesson copy is separate from your provider's unsubscribe footer, which you must retain.

Add an illustration only when it explains the lesson. Put it next to the relevant instructions rather than above an unrelated introduction. Use a public-safe visual style of your own; this workflow does not include a private brand recipe. In the permission lesson, the diagram belongs before the API-key and connector guidance, followed by a plain explanation of the available editing route.

Validate on desktop and a narrow phone preview, check every link, and complete the real unconfirmed/confirmed signup test. Save what actually happened rather than calling a configured automation “working.”

## Write and format for the reader

Start with the point rather than a repeated greeting. Explain a new term where
the reader first needs it, then show one concrete example. Explain one useful idea and show how it affects an edit. Offer a prompt when
it makes the advice easier to use; do not assign a daily exercise. Experienced editors
can skip an explanation; beginners should not have to guess a missing step.

Keep paragraphs short, use complete sentences and put copyable prompts in
their own blocks. Use light humor when it helps the explanation. Cut vague
claims and invented results. An illustration should explain the nearby idea,
with enough context to make that idea useful.

Use a comfortable body size, roughly 17 pixels, generous line spacing and
visible paragraph breaks. Keep the reading column about 600 pixels wide on
desktop and make it fit narrow phones. Images should scale to the column,
preserve their aspect ratio and have useful alternative text. Allow long URLs
and prompts to wrap. Test the actual provider preview as well as the source
HTML; the provider adds its own wrapper, footer and tracked links.

The full pack is available on day one. Setup saves a private editing profile
and can finish without footage. Later emails offer advice to use at the
reader's pace. Default to complete requested edits; previews, manual finishing
and staged approval are choices. Do not promise universal editor control or
that saving a profile retrains a model.

## Optional community invitations

The templates include six short invitations in lessons 1, 5, 9, 13, 18 and 22.
Use `YOUR_COMMUNITY_URL` for your own community destination, or remove those
postscripts if your offer has no community. Confirm that the classroom,
questions space and other resources named in each invitation exist before
using the copy. Adapt the resource claims and instructor wording to your own
offer; these templates do not promise access to someone else's community.

Keep each invitation after the main lesson and signature, separated by a blank
paragraph. Use P.P.S. when the lesson already has a P.S. Preserve the existing
postscript, illustration and main call to action. Space invitations across the
sequence instead of adding one to every email. The existing immediate first
lesson and daily cadence stay the same.

Use the [update checklist](UPDATES.md) when a material change affects the pack,
email lessons or community classroom. A repository update does not change
live emails or classroom pages automatically.
