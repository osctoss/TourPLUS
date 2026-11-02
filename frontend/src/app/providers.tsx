"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { apiClient } from "@/lib/api-client";

interface User {
  id: string;
  email: string;
  role: string;
}

interface PatientProfile {
  id: string;
  full_name: string;
  origin_country_code: string;
  display_currency: string;
}

interface AuthContextType {
  user: User | null;
  profile: PatientProfile | null;
  isLoading: boolean;
  login: (userData: User, profileData?: PatientProfile) => void;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  profile: null,
  isLoading: true,
  login: () => {},
  logout: async () => {},
  refreshUser: async () => {},
});

export const useAuth = () => useContext(AuthContext);

export function Providers({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60 * 1000,
            refetchOnWindowFocus: false,
          },
        },
      })
  );

  const [user, setUser] = useState<User | null>(null);
  const [profile, setProfile] = useState<PatientProfile | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  const refreshUser = async () => {
    try {
      const data: any = await apiClient.get("/auth/me/");
      setUser(data.user);
      setProfile(data.profile);
    } catch {
      setUser(null);
      setProfile(null);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshUser();
  }, []);

  const handleLogin = (userData: User, profileData?: PatientProfile) => {
    setUser(userData);
    if (profileData) setProfile(profileData);
  };

  const handleLogout = async () => {
    try {
      await apiClient.post("/auth/logout/");
    } catch {
      // ignore
    } finally {
      setUser(null);
      setProfile(null);
    }
  };

  return (
    <QueryClientProvider client={queryClient}>
      <AuthContext.Provider
        value={{
          user,
          profile,
          isLoading,
          login: handleLogin,
          logout: handleLogout,
          refreshUser,
        }}
      >
        {children}
      </AuthContext.Provider>
    </QueryClientProvider>
  );
}
