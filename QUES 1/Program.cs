using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;

namespace ContactBookApp
{
    internal class Program
    {
        const int MaxContacts = 20;
        const string StorageFile = "Contacts.txt";

        static void Main(string[] args)
        {
            List<ContactBook> contacts = new List<ContactBook>();

            if (File.Exists(StorageFile))
            {
                try
                {
                    var lines = File.ReadAllLines(StorageFile);
                    foreach (var line in lines)
                    {
                        if (string.IsNullOrWhiteSpace(line)) continue;
                        var c = ContactBook.FromFileFormat(line);
                        if (contacts.Count < MaxContacts)
                            contacts.Add(c);
                    }
                }
                catch (Exception ex)
                {
                    Console.WriteLine($"Warning: Could not load saved contacts: {ex.Message}");
                }
            }

            while (true)
            {
                ShowMainMenu();
                Console.Write("Enter choice: ");
                var choice = Console.ReadLine()?.Trim();

                switch (choice)
                {
                    case "1":
                        AddContact(contacts);
                        break;
                    case "2":
                        ShowAllContacts(contacts);
                        break;
                    case "3":
                        ShowContactDetails(contacts);
                        break;
                    case "4":
                        UpdateContact(contacts);
                        break;
                    case "5":
                        DeleteContact(contacts);
                        break;
                    case "0":
                        SaveContacts(contacts);
                        Console.WriteLine("Exiting. Goodbye!");
                        return;
                    default:
                        Console.WriteLine("Invalid option. Enter 0-5.");
                        break;
                }

                Console.WriteLine();
            }
        }

        static void ShowMainMenu()
        {
            Console.WriteLine("Main Menu");
            Console.WriteLine("1: Add Contact");
            Console.WriteLine("2: Show All Contacts");
            Console.WriteLine("3: Show Contact Details");
            Console.WriteLine("4: Update Contact");
            Console.WriteLine("5: Delete Contact");
            Console.WriteLine("0: Exit");
        }

        static void AddContact(List<ContactBook> contacts)
        {
            if (contacts.Count >= MaxContacts)
            {
                Console.WriteLine($"Contact book full (maximum {MaxContacts} contacts).");
                return;
            }

            Console.WriteLine($"\nEnter details for Contact #{contacts.Count + 1}:");
            ContactBook contact = new ContactBook();

            Console.Write("First Name: ");
            contact.FirstName = Console.ReadLine();

            Console.Write("Last Name: ");
            contact.LastName = Console.ReadLine();

            Console.Write("Company: ");
            contact.Company = Console.ReadLine();

            Console.Write("Email: ");
            contact.Email = Console.ReadLine();

            Console.Write("Birth Date (dd/MM/yyyy): ");
            contact.BirthDate = Console.ReadLine();

            while (true)
            {
                Console.Write("Mobile Number (9 digits, cannot start with 0): ");
                string? mobileInput = Console.ReadLine();

                if (mobileInput != null && contact.SetMobileNumber(mobileInput))
                {
                    break; 
                }
                else
                {
                    Console.WriteLine("Invalid mobile number. Please try again.");
                }
            }

            contacts.Add(contact);
            Console.WriteLine("Contact added.");
        }


        static void ShowAllContacts(List<ContactBook> contacts)
        {
            Console.WriteLine("\n--- All Contacts ---");
            if (contacts.Count == 0)
            {
                Console.WriteLine("No contacts found.");
                return;
            }

            for (int i = 0; i < contacts.Count; i++)
            {
                Console.WriteLine($"{i + 1}. {contacts[i].GetSummary()}");
            }
        }


        static void ShowContactDetails(List<ContactBook> contacts)
        {
            Console.Write("Find by (1) index or (2) mobile? Enter 1 or 2: ");
            var opt = Console.ReadLine()?.Trim();
            if (opt == "1")
            {
                int idx = ReadInt("Enter contact index (1-based): ");
                if (idx < 1 || idx > contacts.Count) Console.WriteLine("Invalid index.");
                else contacts[idx - 1].ShowContact();
            }
            else if (opt == "2")
            {
                Console.Write("Enter mobile number: ");
                var mobile = Console.ReadLine();
                var found = contacts.FirstOrDefault(x => x.MobileNumber == mobile);
                if (found == null) Console.WriteLine("No contact found with that mobile number.");
                else found.ShowContact();
            }
            else
            {
                Console.WriteLine("Invalid choice.");
            }
        }

 
        static void UpdateContact(List<ContactBook> contacts)
        {
            int idx = ReadInt("Enter contact index to update (1-based): ");
            if (idx < 1 || idx > contacts.Count)
            {
                Console.WriteLine("Invalid index.");
                return;
            }

            var target = contacts[idx - 1];
            Console.WriteLine("Leave blank to keep current value.");

            Console.Write($"First Name ({target.FirstName}): ");
            var s = Console.ReadLine();
            if (!string.IsNullOrWhiteSpace(s)) target.FirstName = s;

            Console.Write($"Last Name ({target.LastName}): ");
            s = Console.ReadLine();
            if (!string.IsNullOrWhiteSpace(s)) target.LastName = s;

            Console.Write($"Company ({target.Company}): ");
            s = Console.ReadLine();
            if (!string.IsNullOrWhiteSpace(s)) target.Company = s;

            Console.Write($"Email ({target.Email}): ");
            s = Console.ReadLine();
            if (!string.IsNullOrWhiteSpace(s)) target.Email = s;

            Console.Write($"Birth Date ({target.BirthDate}): ");
            s = Console.ReadLine();
            if (!string.IsNullOrWhiteSpace(s)) target.BirthDate = s;

            Console.Write("Change mobile number? (y/n): ");
            var ans = Console.ReadLine();
            if (ans?.Trim().ToLower() == "y")
            {
                while (true)
                {
                    Console.Write("Enter new mobile number (9 digits, cannot start with 0): ");
                    var m = Console.ReadLine();
                    if (m != null && target.SetMobileNumber(m))
                    {
                        Console.WriteLine("Mobile updated.");
                        break;
                    }
                    Console.WriteLine("Invalid mobile. Try again.");
                }
            }

            Console.WriteLine("Contact updated.");
        }


        static void DeleteContact(List<ContactBook> contacts)
        {
            int idx = ReadInt("Enter contact index to delete (1-based): ");
            if (idx < 1 || idx > contacts.Count)
            {
                Console.WriteLine("Invalid index.");
                return;
            }

            Console.Write($"Are you sure you want to delete contact #{idx}? (y/n): ");
            var ans = Console.ReadLine();
            if (ans?.Trim().ToLower() == "y")
            {
                contacts.RemoveAt(idx - 1);
                Console.WriteLine("Contact deleted.");
            }
            else
            {
                Console.WriteLine("Delete cancelled.");
            }
        }
        static void SaveContacts(List<ContactBook> contacts)
        {
            try
            {
                var lines = contacts.Select(c => c.ToFileFormat()).ToArray();
                File.WriteAllLines(StorageFile, lines);
                Console.WriteLine($"Contacts saved to {StorageFile}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error saving contacts: {ex.Message}");
            }
        }
        static int ReadInt(string prompt)
        {
            while (true)
            {
                Console.Write(prompt);
                var s = Console.ReadLine();
                if (int.TryParse(s, out int v)) return v;
                Console.WriteLine("Please enter a valid number.");
            }
        }
    }
}
