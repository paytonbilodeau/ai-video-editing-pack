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

Set the post-confirmation destination to your pack's setup URL. Set the signup success message to “Check your inbox and confirm your email. Then I’ll send your first lesson and open the editing pack.” Customize the confirmation copy in [CONFIRMATION.md](CONFIRMATION.md). Use [settings.example.json](settings.example.json) as a checklist, not an API payload. No live account IDs are supplied.

Before launch, authenticate your sending domain using the provider's current instructions. Check the received email's SPF, DKIM and DMARC results, unsubscribe behavior, sender identity and reply address. Double opt-in improves consent and list quality; it cannot guarantee Inbox or Primary placement. Test with your own address and inspect a real received message.

## The 22 lessons

[The sequence map](SEQUENCE.md) links all lesson templates. Customize the instructor name, URLs and first-person examples before importing. Those examples come from the original guide; use only experiences and results you can honestly claim. The lesson copy is separate from your provider's unsubscribe footer, which you must retain.

Add an illustration only when it explains the lesson. Put it next to the relevant instructions rather than above an unrelated introduction. Use a public-safe visual style of your own; this workflow does not include a private brand recipe. In the permission lesson, the diagram belongs before the API-key and connector guidance, then the copied-clip test.

Validate on desktop and a narrow phone preview, check every link, and complete the real unconfirmed/confirmed signup test. Save what actually happened rather than calling a configured automation “working.”
