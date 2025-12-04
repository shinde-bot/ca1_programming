using System;
using System.Collections.Generic;

class FileExtensionInfo
{
    static void Main()
    {
        Dictionary<string, string> fileExtensions = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase)
        {
            { ".mp4", "MPEG-4 Video File" },
            { ".mov", "Apple QuickTime Movie" },
            { ".avi", "Audio Video Interleave File" },
            { ".mkv", "Matroska Video File" },
            { ".webm", "WebM Video File" },
            { ".jpg", "JPEG Image" },
            { ".jpeg", "JPEG Image" },
            { ".png", "Portable Network Graphics" },
            { ".gif", "Graphics Interchange Format" },
            { ".bmp", "Bitmap Image" },
            { ".txt", "Plain Text File" },
            { ".doc", "Microsoft Word Document" },
            { ".docx", "Microsoft Word Open XML Document" },
            { ".xls", "Microsoft Excel Spreadsheet" },
            { ".xlsx", "Microsoft Excel Open XML Spreadsheet" },
            { ".ppt", "Microsoft PowerPoint Presentation" },
            { ".pptx", "Microsoft PowerPoint Open XML Presentation" },
            { ".pdf", "Portable Document Format" },
            { ".zip", "Compressed Archive" },
            { ".rar", "WinRAR Compressed Archive" }
        };

        Console.WriteLine("File Extension Information System");
        Console.WriteLine("Type 'exit' to quit.");
        
        while (true)
        {
            Console.Write("\nEnter a file extension (e.g., .mp4): ");
            string input = Console.ReadLine().Trim();

            if (input.Equals("exit", StringComparison.OrdinalIgnoreCase))
            {
                Console.WriteLine("Exiting program. Goodbye!");
                break;
            }

            if (!input.StartsWith("."))
            {
                input = "." + input;
            }

            if (fileExtensions.TryGetValue(input, out string description))
            {
                Console.WriteLine($"{input} : {description}");
            }
            else
            {
                Console.WriteLine($"Sorry, information for '{input}' is not available.");
            }
        }
    }
}

