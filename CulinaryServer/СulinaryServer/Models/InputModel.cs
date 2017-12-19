using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace СulinaryServer.Models
{
    public class InputModel
    {
       public string Name { get; set; }
    }

    public class InputModelArray
    {
        public List<InputModel> Items { get; set; }
    }

}

