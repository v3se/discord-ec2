# Joining the Valheim Server

This server is private and only reachable over Tailscale — it will not show up in the
public Steam server browser. Follow these steps to get connected.

## 1. Accept your invite

You'll receive an email invite to join a Tailscale network (tailnet). Click the link,
and sign in / create a Tailscale account using **that same email address**.

## 2. Install Tailscale

Install the Tailscale client for your platform and sign in with the account from step 1:

- Windows / macOS / Linux: https://tailscale.com/download
- Once installed, make sure it shows as **Connected**.

## 3. Confirm you're connected

Run this to check your connection:

```
tailscale status
```

You should see `valheim-server` listed as a peer. If you don't see it, wait a minute and
re-run `tailscale status`, or try `tailscale up` again. If it's still missing, contact
the server admin — you may not be added to the access list yet.

You can also test the tunnel directly:

```
tailscale ping valheim-server
```

## 4. Get the connection details from the admin

You'll need:
- **Server IP**: `100.x.y.z` (ask the admin — this is the Tailscale IP, not a public address)
- **Port**: `2456`
- **Server password**

## 5. Connect in Valheim

The server is private, so it won't appear in the normal server browser. In Valheim:

1. Main Menu → **Start Game**
2. **Join Game** → **Add Server** / **Direct Connect** (depending on game version)
3. Enter `100.x.y.z:2456`
4. Enter the server password when prompted

## Troubleshooting

- **Can't see `valheim-server` in `tailscale status`**: You haven't been added to the
  access list yet, or your Tailscale login email doesn't match what the admin added —
  double check with the admin.
- **`tailscale ping` times out**: Tailscale itself isn't connecting. Check Tailscale is
  running and signed in, and that you have internet access.
- **Tailscale connects, but Valheim won't join**: Double check the IP, port, and
  password. Confirm with the admin that the server is actually running.

---

# For the admin: enrolling a new player

1. **Invite them to the tailnet**: Tailscale admin console → Users → Invite member,
   using their email.
2. **Add them to the access group**: edit the tailnet ACL policy, add their exact
   Tailscale login email to `group:friends`:
   ```json
   "groups": {
       "group:friends": ["friend1@example.com", "newfriend@example.com"],
   },
   ```
   Save — this applies immediately.
3. Send them this document and the connection details (IP/port/password from the
   `valheim-server` machine in the admin console).
4. **To revoke access**, remove their email from `group:friends` and save.

## Verifying a player can reach *only* the Valheim server

Don't just confirm they can connect — confirm they can't reach anything else:

- **Peer visibility**: on their device, `tailscale status` should list `valheim-server`
  and nothing else from your infrastructure. Tailscale only shows peers a device has an
  ACL grant to see.
- **Negative test**: have them (or you, via `tailscale ping` from a device tagged
  `tag:friends`) try to reach another tagged node, e.g. `tag:management` or
  `tag:app` — it should fail outright (no route), not just be firewalled.
- **Built-in ACL tests**: add a `tests` block to the policy file itself — Tailscale
  validates these on every save and refuses to save if they fail, so it's a permanent
  regression check:
  ```json
  "tests": [
      {
          "src": "newfriend@example.com",
          "accept": ["tag:valheim-server:2456"],
          "deny": ["tag:management:*", "tag:app:*"]
      }
  ]
  ```
- **Port scope**: confirm the grant is limited to `2456-2457`, not `tag:valheim-server:*`
  — an overly broad destination would also expose port 9001 (the supervisor/admin web UI)
  to friends.

## Testing the Valheim server and connection end-to-end

On the server node / via Portainer:
- `docker service logs <stack>_valheim` — look for the server finishing world load
  (no repeated crash/restart loops).
- `docker service ps <stack>_valheim` and `<stack>_valheim-tailscale` — confirm both
  are `Running` and scheduled on the pinned node.
- `docker service logs <stack>_valheim-tailscale` — confirm it registered with the
  tailnet and shows the `valheim-server` hostname/tags.
- On the host: `ss -lunp | grep 2456` — confirms something is actually listening on
  the UDP game ports.

From a tailnet device (yours or a friend's):
- `tailscale ping valheim-server` — confirms the Tailscale tunnel itself is up
  (and whether it's direct or relayed via DERP, which affects latency).
- Launch Valheim and do a real direct-connect join using the IP:port/password —
  this is the only test that verifies the full path (network + game handshake +
  password + world state), so do this at least once after any change.
- Optional lightweight check without launching the game: a Steam A2S server-query
  tool (e.g. `python -m a2s` or similar) against `100.x.y.z:2456` can confirm the
  server is answering queries without needing to fully join.
