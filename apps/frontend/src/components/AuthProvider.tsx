"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { loginUserApi, registerUserApi } from "@/lib/api";

type AuthContextType = {
  isAuthenticated: boolean;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  registerUser: (email: string, password: string) => Promise<void>;
};

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  token: null,
  login: async () => {},
  registerUser: async () => {},
});

export const AuthProvider = ({ children }: { children: React.ReactNode }) => {
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    // Load token from localStorage on mount
    const storedToken = localStorage.getItem("access_token");
    if (storedToken) setToken(storedToken);
  }, []);

  const login = async (email: string, password: string) => {
    const newToken = await loginUserApi(email, password);
    setToken(newToken);
    localStorage.setItem("access_token", newToken);
  };

  const registerUser = async (email: string, password: string) => {
    await registerUserApi(email, password);
  };

  // const isAuthenticated = !!token;
  const isAuthenticated = true;

  return (
    <AuthContext.Provider
      value={{
        isAuthenticated,
        token,
        login,
        registerUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export function useAuth() {
  return useContext(AuthContext);
}

export default AuthProvider;
