/* Cookie / storage consent (vanilla-cookieconsent v3, MIT).
 * Categories are honest: this site sets no tracking cookies. "Functional"
 * gates the localStorage used to remember recent workspaces on the
 * sign-in page. Other scripts check window.ejConsent.functional().
 */
(function () {
  "use strict";
  if (!window.CookieConsent) return;

  window.ejConsent = {
    functional: function () {
      try {
        return window.CookieConsent.acceptedCategory("functional");
      } catch (e) {
        return false;
      }
    },
  };

  window.CookieConsent.run({
    // Consent UI is rendered only after a choice is required; the cookie
    // it stores ("ej_consent") is itself strictly necessary.
    cookie: { name: "ej_consent", expiresAfterDays: 182 },
    guiOptions: {
      consentModal: {
        layout: "box",
        position: "bottom left",
        equalWeightButtons: true,
        flipButtons: false,
      },
      preferencesModal: { layout: "box", equalWeightButtons: true },
    },
    categories: {
      necessary: { enabled: true, readOnly: true },
      functional: {
        enabled: true,
        autoClear: { cookies: [] },
      },
    },
    onConsent: function () {
      // Drop remembered workspaces if functional storage was declined.
      if (!window.ejConsent.functional()) {
        try { localStorage.removeItem("everjust.recentWorkspaces"); } catch (e) {}
      }
    },
    onChange: function () {
      if (!window.ejConsent.functional()) {
        try { localStorage.removeItem("everjust.recentWorkspaces"); } catch (e) {}
      }
    },
    language: {
      default: "en",
      translations: {
        en: {
          consentModal: {
            title: "Your data, your call",
            description:
              "EVERJUST.APP sets no tracking or advertising cookies. We use one " +
              "strictly necessary cookie to remember this choice, and optional " +
              "on-device storage to remember your recent workspaces on the " +
              "sign-in page. <a href=\"/privacy\">Privacy policy</a>",
            acceptAllBtn: "Accept all",
            acceptNecessaryBtn: "Necessary only",
            showPreferencesBtn: "Manage preferences",
          },
          preferencesModal: {
            title: "Privacy preferences",
            acceptAllBtn: "Accept all",
            acceptNecessaryBtn: "Necessary only",
            savePreferencesBtn: "Save preferences",
            closeIconLabel: "Close",
            sections: [
              {
                title: "How EVERJUST.APP handles your data",
                description:
                  "No analytics, no ad trackers, no third-party cookies. " +
                  "Workspace data lives in your own isolated database. " +
                  "Full details in the <a href=\"/privacy\">privacy policy</a>.",
              },
              {
                title: "Strictly necessary",
                description:
                  "Required for the site to function: your session on your " +
                  "workspace, security protections, and the cookie that " +
                  "remembers this consent choice.",
                linkedCategory: "necessary",
              },
              {
                title: "Functional storage",
                description:
                  "Remembers the workspaces you've signed in to on this " +
                  "device so the sign-in page can offer one-tap shortcuts. " +
                  "Stored only in your browser, never sent to us.",
                linkedCategory: "functional",
              },
              {
                title: "Questions?",
                description:
                  "Email <a href=\"mailto:company@everjust.co\">company@everjust.co</a> " +
                  "— a human answers.",
              },
            ],
          },
        },
      },
    },
  });
})();
