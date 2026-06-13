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

Reference log output L20 in `oauth/exercise_two.out`

Final: I have created a unit test for the `_validate_token_request` method in the `AuthorizationServer` class. Reference `dsdx/tests/test_authorization_server.py` -> `test_validate_token_request`

### Three:

> Trace through the PKCE flow for this interception scenario:
An attacker has intercepted the authorization code but does not know the code verifier.
What happens when the attacker sends the code to the token endpoint without a verifier?
What happens if the attacker sends the code with a wrong verifier?
Verify by modifying `PKCEClient._exchange_code` to send a tampered verifier.
> 

*TODO*

### Four:

> The client credentials flow is used for machine-to-machine authentication.
    Modify `ClientCredentialsClient` to automatically retry token acquisition
    if the first attempt fails, with exponential backoff.
    What should the retry limit be, and why?
> 

Idea: In **`client_credentials.py` L**106 of the invalid section of the control flow, we attempt retries (while loop true) with exponential timings of sleep between with a max of 3 retries per attempt. 3 at the moment is arbitrary, and a conservative limit to not overload the auth request queue.

  >A standard, well-documented exponential backoff for token acquisition uses: an initial delay, an exponential multiplier per retry, optional random jitter, a maximum delay cap, and a maximum retry count (or overall timeout). Use jitter to avoid thundering-herd. Common variants: full jitter, equal jitter, and decorrelated jitter (recommended by AWS).
  
  Example (clear, language-agnostic algorithm + Go and Python examples):
  
  Algorithm (parameters)
  - initial = base delay (e.g., 500 ms)
  - factor = multiplier (usually 2)
  - maxDelay = cap (e.g., 30 s)
  - maxRetries = maximum attempts (e.g., 5)
  - jitter = true (use randomized jitter)
  - backoff(i) for attempt i (0-based) = min(maxDelay, initial * factor^i) then apply jitter variant
  
  Jitter variants
  - Full jitter: sleep = random(0, backoff(i))
  - Equal jitter: sleep = backoff(i)/2 + random(0, backoff(i)/2)
  - Decorrelated jitter (per attempt): sleep = min(maxDelay, random(initial, previousSleep * 3))
  
  Recommended: use Full jitter or Decorrelated jitter (AWS SDK recommends decorrelated or full jitter to reduce spikes).
  
  With decorrelated jitter
  ```python
  import random
  import time
  
  def acquire_token_with_backoff(fetch):
      initial = 0.5          # seconds
      max_delay = 30.0       # seconds
      max_retries = 5
  
      sleep = initial
      last_exc = None
      for attempt in range(max_retries):
          try:
              return fetch()
          except Exception as e:
              last_exc = e
              # decorrelated jitter
              sleep = min(max_delay, random.uniform(initial, sleep * 3))
              time.sleep(sleep)
      raise RuntimeError("token acquisition failed") from last_exc
  ```

Implementation notes:
  We have our main private method `_acquire_token()`. We have a single failure token response check. To integrate exponential backoff, I can begin the algorithm at L96, after creating the request object. We enter the loop for max retries. We won't raise an exception, we'll keep the output currently in place on L107.

*What should the retry limit be, and why?*
A max retry limit is in place to not have an indefinite request loop (expand...). Currently 5 is in place.

### Five:

> Access tokens expire (after 60 seconds in the simulation).
    What happens if a client tries to use an expired token?
    Trace through `resource_server.py` to find the expiry check.
    Now modify `OAuthClient` to detect a token-expired error in the resource response
    and automatically request a new token before retrying.
    (This is the "token refresh" pattern; you can use a refresh token or re-run the full flow.)
> 

Idea, create request flow for simultaneous new and refresh token. When auth token is expired, check that the client has an associated refresh token that is valid, if true initiate creation of new auth token. Else, return auth error of expired tokens.

Control flow:
  -> `oauth_client`: 
    -> `access_resource()`
      -> failure flow: `access_resource()` will return response
    -> `run()`: check for `response.error` == `token_expired`
    -> new attr `self.refresh_token`
    -> new `exchange_refresh_token_for_token()`, parameters will be `self.refresh_token`, return `TokenResponse`
      -> token response check as is currently in place for refresh token failure.
    -> Expand `TokenRequest`: new attr `refresh_token`
    -> new resource request with new refresh token.
  -> `authorization_server`: `_validate_token_request()` add return type `RefreshToken`
    -> check for `request.code` presence for auth_code validation flow
    -> check for `request.refresh_token` presence for refresh_token validation flow
    -> `handle_token_request()` will check object type AuthorizationCode or RefreshToken
      -> if code, go through `_issue_access_token_via_code()`, a rename of `_issue_access_token()`
        -> also create `RefreshToken` and add to `self.refresh_tokens`
        -> add new refresh token to `TokenResponse`
      -> if refresh token, create new `AccessToken` and `TokenResponse` with new token and current refresh token.
