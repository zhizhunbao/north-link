/**
 * Auth API service — AUTH-006.
 */
import { api } from "./api";

export interface PasswordChangeData {
  old_password: string;
  new_password: string;
}

export const authService = {
  changePassword: (data: PasswordChangeData) =>
    api.put("/api/v1/auth/password", data),

  getProfile: () =>
    api.get("/api/v1/auth/me"),
};
