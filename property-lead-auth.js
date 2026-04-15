(function () {
  const config = window.PROPERTY_LEAD_ADVISOR_AUTH || {};
  const hasConfig = Boolean(config.supabaseUrl && config.supabaseAnonKey);
  const auth = {
    ready: false,
    configured: hasConfig,
    client: null,
    async getSession() {
      if (!this.ready || !this.client) return null;
      const { data } = await this.client.auth.getSession();
      return data.session;
    },
    async signIn(email, password) {
      if (!this.ready || !this.client) {
        return { error: new Error("Auth is not configured yet.") };
      }
      return this.client.auth.signInWithPassword({ email, password });
    },
    async signOut() {
      if (!this.ready || !this.client) return;
      return this.client.auth.signOut();
    },
    onChange(callback) {
      if (!this.ready || !this.client) return () => {};
      const { data } = this.client.auth.onAuthStateChange((_event, session) => {
        callback(session);
      });
      return () => data.subscription.unsubscribe();
    }
  };

  if (hasConfig && window.supabase && typeof window.supabase.createClient === "function") {
    auth.client = window.supabase.createClient(config.supabaseUrl, config.supabaseAnonKey);
    auth.ready = true;
  }

  window.PropertyLeadAuth = auth;
})();
