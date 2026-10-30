### Deploy to Vercel

> Config environments
>
> ```bash
> # Random secret
> GITHUB_WEBHOOK_SECRET
>
> # Discord Webhook URL
> DISCORD_WEBHOOK_URL
>
> # Telegram Bot and Chat
> BOT_TOKEN
> CHAT_ID
> ```

---

### Config Github Webhook

> Payload URL
>
> ```
> https://<your-project>.vercel.app/webhook
> ```

> Content type
>
> ```
> application/json
> ```

> Secret
>
> ```
> <Same GITHUB_WEBHOOK_SECRET>
> ```

> Which events would you like to trigger this webhook?
>
> ```bash
> # Select Let me select individual events.
> - Issue comments
> - Pull request reviews
> - Pull requests
> - Workflow runs
> ```
