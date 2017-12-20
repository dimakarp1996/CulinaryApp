using System;
using System.Diagnostics;
using System.Collections.Generic;
using System.Configuration;
using System.IO;
using System.Linq;
using System.Net;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using СulinaryServer.Models;
using IronPython.Hosting;
using Microsoft.Scripting.Hosting;
namespace СulinaryServer
{
    class Program
    {
        private static string _url;
        private static string _port;
        private static string _pythonDir;
        static void Main(string[] args)
        {
            _url = ConfigurationManager.AppSettings["url"];
            _port = ConfigurationManager.AppSettings["port"];
            _pythonDir = ConfigurationManager.AppSettings["python_path"];

            var _prefix = String.Format("{0}:{1}/", _url, _port);

            HttpListener listener = new HttpListener();
            listener.Prefixes.Add(_prefix);

            listener.Start();
            
            Console.WriteLine("Вы зашли в CulinaryApp REST api.\n", _port);
            Console.WriteLine("", _prefix);
            Console.WriteLine("Сделайте POST запрос вида i с одним из индексов категории в качестве i");
            Console.WriteLine("Индекс категории Закуски - 0");
            Console.WriteLine("Индекс категории Напитки - 1");
            Console.WriteLine("Индекс категории Завтраки - 2");
            Console.WriteLine("Индекс категории Супы - 3");
            Console.WriteLine("Индекс категории Салаты - 3");
            Console.WriteLine("Индекс категории Выпечка и десерты - 5");
            Console.WriteLine("Индекс категории Ризотто - 6");
            Console.WriteLine("Индекс категории Бульоны - 7");
            Console.WriteLine("Индекс категории Паста и пицца - 8");
            Console.WriteLine("Индекс категории Основные блюда - 9");
            Console.WriteLine("Индекс категории Сэндвичи - 10");
            Console.WriteLine("Индекс категории Соусы и маринады - 11");
            int i = 0;
            while (i==0)
            {
                //Ожидание входящего запроса
                HttpListenerContext context = listener.GetContext();
                //Объект запроса
                HttpListenerRequest request = context.Request;
                //Объект ответа
                HttpListenerResponse response = context.Response;
                //читаем содержимое
                var input = new StreamReader(context.Request.InputStream).ReadToEnd();

                //InputModelArray inputModelArray = (InputModelArray)JsonConvert.DeserializeObject(body , typeof(InputModelArray));

                //вызываем скрипт и получаем результат
                //var output = RunPythonProgram(input,"script3");
                Console.WriteLine("В консоль передана команда:");
                Console.WriteLine("C://CulinaryApp//REST_API_SCRIPT.py " + input);
                Console.WriteLine("Ваш запрос обрабатывается - ждите");
                Console.WriteLine(input);
                var output = run_cmd("C://CulinaryApp//REST_API_SCRIPT.py " + input);
                Console.WriteLine("Из-за возможных проблем с кодировкой, список ингредиентов записан в C://CulinaryApp//");
                //Создаем ответ
                //Console.WriteLine("{0} request was caught: {1}",request.HttpMethod, request.Url);
                Console.WriteLine(output);
                response.StatusCode = (int)HttpStatusCode.OK;
                byte[] b = Encoding.UTF8.GetBytes(output.ToString());
                response.ContentLength64 = b.Length;
                response.OutputStream.Write(b, 0, b.Length);
                using (Stream stream = response.OutputStream) { }
                response.OutputStream.Close();
                Console.WriteLine("Сделайте POST запрос вида индекс продукт1,продукт2,продукт3,... с одним из названий продуктов в качестве продукт1 ,продукт2, продукт3 и т д");
                Console.WriteLine("Используйте только те названия продуктов, которые есть в файле,cозданном в директории C://CulinaryApp");
                Console.WriteLine("Индекс вводите тот же, что и ранее");
                //Ожидание входящего запроса
                HttpListenerContext context1 = listener.GetContext();
                //Объект запроса
                HttpListenerRequest request1 = context1.Request;
                //Объект ответа
                HttpListenerResponse response1 = context1.Response;
                //читаем содержимое
                var input1 = new StreamReader(context1.Request.InputStream).ReadToEnd();



                Console.WriteLine("В консоль передана команда:");
                Console.WriteLine("C://CulinaryApp//REST_API_SCRIPT.py " + input);
                Console.WriteLine("Ваш запрос обрабатывается - ждите");
                var output1 = run_cmd("C://CulinaryApp//REST_API_SCRIPT.py "+input1);
                //Создаем ответ
                Console.WriteLine("{0} request was caught: {1}", request.HttpMethod, request.Url);

                response.StatusCode = (int)HttpStatusCode.OK;


                Console.WriteLine("3 самых похожих рецепта найдены и лежат по адресу C://CulinaryApp//Receipts.txt");
                //Возвращаем ответ
                using (Stream stream = response.OutputStream) { }
                response.OutputStream.Close();
                Console.WriteLine("Нажмите любую кнопку");
                char c = Console.ReadKey().KeyChar;
                i = 1;
                
            }
           
        }

        public static string run_cmd(string cmd)
        {
            ProcessStartInfo start = new ProcessStartInfo();
            start.FileName = _pythonDir;
            start.Arguments = cmd; //string.Format("\"{0}\" \"{1}\"", cmd, args);
            start.UseShellExecute = false;// Do not use OS shell
            start.CreateNoWindow = false; // We don't need new window
            start.RedirectStandardOutput = true;// Any output, generated by application will be redirected back
            start.RedirectStandardError = true; // Any error in standard output will be redirected back (for example exceptions)
            
            using (Process process = Process.Start(start))
            {
                using (StreamReader reader = process.StandardOutput)
                {
                    string stderr = process.StandardError.ReadToEnd(); // Here are the exceptions from our Python script
                    Console.WriteLine(stderr);
                    string result = reader.ReadToEnd(); // Here is the result of StdOut(for example: print "test")
                    Console.WriteLine(result);
                    return result;
                }
            }
        }
    }
}
