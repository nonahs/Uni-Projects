// namespace: A4CS
// service class: A4CS

using System;
using System.Collections.Generic;
using System.Data.Services;
using System.Data.Services.Common;
using System.Data.Services.Providers;
using System.Linq;
using System.ServiceModel;
using System.ServiceModel.Web;

using System.Web;
using System.Xml.Linq;

namespace A4CS {
    [ServiceBehavior(IncludeExceptionDetailInFaults = true)]
    public class A4CS : DataService<DataSource> {
        public static void InitializeService(DataServiceConfiguration config) {
            config.SetEntitySetAccessRule("*", EntitySetRights.AllRead);
            config.DataServiceBehavior.MaxProtocolVersion = DataServiceProtocolVersion.V3;
            config.UseVerboseErrors = true;

        }
    }

    [DataServiceKey("CustomerID")]
    public class Customer {
        public string CustomerID { get; set; }
        public string CompanyName { get; set; }
        public string ContactName { get; set; }
        public IEnumerable<Order> Orders { get; set; }
    }

    [DataServiceKey("OrderID")]
    public class Order {
        public int OrderID { get; set; }
        public string CustomerID { get; set; }
        public DateTime? OrderDate { get; set; }
        public DateTime? ShippedDate { get; set; }
        public decimal? Freight { get; set; }
        public string ShipName { get; set; }
        public string ShipCity  { get; set; }
        public string ShipCountry { get; set; }
        public Customer Customer { get; set; }
    }

    public class DataSource {
        static string FOLDER = HttpContext.Current.Server.MapPath(@".\data");

        static DataSource() {
            Console.WriteLine($"... loading {FOLDER}\\XCustomers.xml");
            _Customers =
                XElement.Load(FOLDER + @"\XCustomers.xml")
                .Elements("Customer")
                .Select(x => new Customer {
                    CustomerID = (string)x.Element("CustomerID"),
                    CompanyName = (string)x.Element("CompanyName"),
                    ContactName = (string)x.Element("ContactName"),
                }).ToArray();

                Console.WriteLine($"... loading {FOLDER}\\XOrders.xml");
                _Orders = 
                    XElement.Load(FOLDER + @"\XOrders.xml")
                    .Elements("Order")
                    .Select(x => new Order {
                        OrderID = (int)x.Element("OrderID"),
                        CustomerID = (string)x.Element("CustomerID"),
                        OrderDate = string.IsNullOrEmpty((string)x.Element("OrderDate")) ? null : (DateTime?)x.Element("OrderDate"),
                        ShippedDate = string.IsNullOrEmpty((string)x.Element("ShippedDate")) ? null : (DateTime?)x.Element("ShippedDate"),
                        Freight = string.IsNullOrEmpty((string)x.Element("Freight")) ? null : (decimal?)x.Element("Freight"),
                        ShipName = (string)x.Element("ShipName"),
                        ShipCity = (string)x.Element("ShipCity"),
                        ShipCountry = (string)x.Element("ShipCountry"),
                    }).ToArray();

                Console.WriteLine($"... relating _Customers with _Orders");

                var _orders_lookup = _Orders.ToLookup(o => o.CustomerID);
                var _customers_dict = _Customers.ToDictionary(c => c.CustomerID);

                foreach (var o in _Orders) o.Customer = _customers_dict[o.CustomerID];
                foreach (var c in _Customers) c.Orders = _orders_lookup[c.CustomerID];

                Console.WriteLine($"... starting");
        }

        static IEnumerable<Customer> _Customers;
        static IEnumerable<Order> _Orders;

        public IQueryable<Customer> Customers {
            get {
                Console.WriteLine($"... returning Customers");
                return _Customers.AsQueryable();
            }
        }

        public IQueryable<Order> Orders {
            get {
                Console.WriteLine($"... returning Orders");
                return _Orders.AsQueryable();
            }
        }

    }
}