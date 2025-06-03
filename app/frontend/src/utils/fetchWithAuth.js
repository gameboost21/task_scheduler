export async function fetchWithAuth(url, options = {}) {
    const token = localStorage.getItem("token");
    if (!token) throw new Error("No token available");

    const headers = {
        ...options.headers,
        Authorization: `Bearer ${token}`,
    };

    return fetch(url, {
        ...options,
        headers,
    });
}