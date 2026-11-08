/**
 * UserObject.ts - org.telegram.messenger.UserObject
 */

import { User } from '../types';

export class UserObject {
  public static getUserName(user?: User | null): string {
    if (!user) return '';
    return [user.first_name, user.last_name].filter(Boolean).join(' ') || user.name || user.username || user.phone || 'User';
  }

  public static isDeleted(user?: User | null): boolean {
    return false;
  }

  public static isUserSelf(user?: User | null): boolean {
    return false;
  }
}
