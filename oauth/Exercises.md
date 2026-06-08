# DSDX - Distributed Systems Design by Example

---

# OAuth

TODO: Create MD file with sectioned exercise responses for references to code modifications.

## Exercises:

### One:

> In the basic OAuth simulation, the authorization server accepts any redirect URI that was pre-registered. Modify the example to register two redirect URIs for `photo_app`: `"https://photo.example.com/callback"` and `"https://photo.example.com/mobile"`. Verify that a request with a URI that is not in the registered list is rejected. 
Why is this check important?
> 

In `oauth/ex_basic_oauth.py` L24, make a list that contains both the callback and the `/mobile` uri.

Pass it into L27 args for `redirecturis` to register them both.

In `_validate_auth_request` in the `AutherizationServer` class, there is a redirect uri check in L95.

To test invalid uri rejection, create a second OAuth client in `oauth/ex_basic_oauth.py` and pass in a test uri for the uris param. Failure will be immediate upon attempting a code request.

**Important:** We don’t under any circumstances want to return an authorization code that can be exchanged for a token to an unauthorized/unrecognized return recipient. Client id and secret could be compromised, but an unknown redirect gatekeeps where we return valid codes/tokens.

### Two:

> The authorization code is single-use.
Find the line in `authorization_server.py` that marks a code as used.
What would happen if this line were removed?
Write a test that reuses the same code twice and verify that the second use fails.
> 

In L181 in `oauth/authorization_server.py` we find an auth code being marked as used first thing before creating and responding with a newly generated token.

If removed, we could create an indefinite amount of authorization tokens for the scoped access that was requested with relevant auth code.

In `oauth/oauth_client.py` after L51, we call `exchange_code_for_token` once more with the exact same auth code. Response should be error after check in the auth server in L158.

### Three:

> Trace through the PKCE flow for this interception scenario:
An attacker has intercepted the authorization code but does not know the code verifier.
What happens when the attacker sends the code to the token endpoint without a verifier?
What happens if the attacker sends the code with a wrong verifier?
Verify by modifying `PKCEClient._exchange_code` to send a tampered verifier.
> 

UMMMMMMMM…

### Four:

> The client credentials flow is used for machine-to-machine authentication.
    Modify `ClientCredentialsClient` to automatically retry token acquisition
    if the first attempt fails, with exponential backoff.
    What should the retry limit be, and why?
> 

Idea: In **`client_credentials.py` L**106 of the invalid section of the control flow, we attempt retries (while loop true) with exponential timings of sleep between with a max of 3 retries per attempt. 3 at the moment is arbitrary, and a conservative limit to not overload the auth request queue.

### Five:

> Access tokens expire (after 60 seconds in the simulation).
    What happens if a client tries to use an expired token?
    Trace through `resource_server.py` to find the expiry check.
    Now modify `OAuthClient` to detect a token-expired error in the resource response
    and automatically request a new token before retrying.
    (This is the "token refresh" pattern; you can use a refresh token or re-run the full flow.)
> 

Idea, create request flow for simultaneous new and refresh token. When auth token is expired, check that the client has an associated refresh token that is valid, if true initiate creation of new auth token. Else, return auth error of expired tokens.
