class Cookie {
  /**
   * Get the value of a cookie by name.
   * @param name - The name of the cookie to retrieve.
   * @returns The cookie value, or null if not found.
   */
  static get(name: string): string | null {
    const cookieString = document.cookie
      .split("; ")
      .find((row) => row.startsWith(`${name}=`));
    return cookieString ? decodeURIComponent(cookieString.split("=")[1]) : null;
  }

  /**
   * Set a cookie with a given name, value, and options.
   * @param name - The name of the cookie.
   * @param value - The value of the cookie.
   * @param options - Additional cookie options.
   */
  static set(
    name: string,
    value: string,
    options: {
      expires?: number | Date; // Number (in days) or a Date object
      path?: string;
      domain?: string;
      secure?: boolean;
    } = {}
  ): void {
    let cookieString = `${encodeURIComponent(name)}=${encodeURIComponent(
      value
    )}`;

    if (options.expires) {
      const expires =
        typeof options.expires === "number"
          ? new Date(Date.now() + options.expires * 24 * 60 * 60 * 1000)
          : options.expires;
      cookieString += `; expires=${expires.toUTCString()}`;
    }

    if (options.path) {
      cookieString += `; path=${options.path}`;
    }

    if (options.domain) {
      cookieString += `; domain=${options.domain}`;
    }

    if (options.secure) {
      cookieString += `; secure`;
    }

    document.cookie = cookieString;
  }

  /**
   * Remove a cookie by name and optional path or domain.
   * @param name - The name of the cookie to remove.
   * @param options - Additional cookie options (path, domain).
   */
  static remove(
    name: string,
    options: { path?: string; domain?: string } = {}
  ): void {
    this.set(name, "", {
      ...options,
      expires: -1, // Set the expiration date to the past to delete the cookie
    });
  }

  /**
   * Update a cookie by name with new value and options.
   * @param name - The name of the cookie to update.
   * @param value - The new value of the cookie.
   * @param options - Additional cookie options.
   */
  static update(
    name: string,
    value: string,
    options: {
      expires?: number | Date;
      path?: string;
      domain?: string;
      secure?: boolean;
    } = {}
  ): void {
    this.set(name, value, options);
  }
}

export default Cookie;
