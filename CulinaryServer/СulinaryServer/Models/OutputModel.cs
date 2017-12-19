using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;

namespace СulinaryServer.Models
{
    public class OutputModel
    {
        [JsonProperty("dish_name")]
        public string name { get; set; }

        [JsonProperty("recipe")]
        public string recipe { get; set; }
    }

    public class OutputModelArray
    {
        public List<OutputModel> Items { get; set; }
    }

}
