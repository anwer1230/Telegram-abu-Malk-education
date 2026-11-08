/**
 * ContactsController.ts - org.telegram.messenger.ContactsController
 */

import { User } from '../../types';

export class ContactsController {
  private static instance: ContactsController;
  public contacts: User[] = [];

  public static getInstance(): ContactsController {
    if (!ContactsController.instance) {
      ContactsController.instance = new ContactsController();
    }
    return ContactsController.instance;
  }

  public loadContacts(): void {
    // Loaded contacts
  }
}
