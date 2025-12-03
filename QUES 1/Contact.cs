using System;
using System.Linq;

namespace ContactBookApp
{
    public class ContactBook
    {
        public string? FirstName { get; set; }
        public string? LastName { get; set; }
        public string? Company { get; set; }
        public string? Email { get; set; }
        public string? BirthDate { get; set; }

        private string? _mobileNumber;
        public string? MobileNumber => _mobileNumber; 
        public bool SetMobileNumber(string num)
        {
            if (!string.IsNullOrWhiteSpace(num))
            {
                num = num.Trim();
                if (num.Length == 9 && num.All(char.IsDigit) && num[0] != '0')
                {
                    _mobileNumber = num;
                    return true;
                }
            }
            return false;
        }

        public void ShowContact()
        {
            Console.WriteLine("\n--- Contact Details ---");
            Console.WriteLine($"First Name : {FirstName}");
            Console.WriteLine($"Last Name  : {LastName}");
            Console.WriteLine($"Company    : {Company}");
            Console.WriteLine($"Mobile No. : {MobileNumber}");
            Console.WriteLine($"Email      : {Email}");
            Console.WriteLine($"Birth Date : {BirthDate}");
        }

        private static string Safe(string? s) => string.IsNullOrEmpty(s) ? "" : s.Replace(",", " ");

        public string ToFileFormat()
        {
            return $"{Safe(FirstName)},{Safe(LastName)},{Safe(Company)},{Safe(Email)},{Safe(BirthDate)},{Safe(MobileNumber)}";
        }

        public static ContactBook FromFileFormat(string line)
        {
            var parts = line.Split(',');
            var c = new ContactBook
            {
                FirstName = parts.Length > 0 ? parts[0] : null,
                LastName  = parts.Length > 1 ? parts[1] : null,
                Company   = parts.Length > 2 ? parts[2] : null,
                Email     = parts.Length > 3 ? parts[3] : null,
                BirthDate = parts.Length > 4 ? parts[4] : null
            };

            if (parts.Length > 5)
                c.SetMobileNumber(parts[5]);

            return c;
        }

        public string GetSummary()
        {
            string name = $"{FirstName ?? ""} {LastName ?? ""}".Trim();
            if (string.IsNullOrEmpty(name)) name = "No Name";
            return $"{name} - {MobileNumber ?? "NoMobile"}";
        }
    }
}
