// namespace: A4FS
// service class: A4FS

namespace A4FS

open System
open System.Collections.Generic
open System.Data.Services
open System.Data.Services.Common
open System.Data.Services.Providers
open System.Linq
open System.ServiceModel
open System.ServiceModel.Web

open System.Web
open System.Xml.Linq

type [<AllowNullLiteral(); DataServiceKey("CustomerID")>]
    Customer () = class
        member val CustomerID: string = null with get, set
        member val CompanyName: string = null with get, set
        member val ContactName: string = null with get, set
        member val Orders: seq<Order> = null with get, set
        end

and [<AllowNullLiteral(); DataServiceKey("OrderID")>]
    Order () = class
        member val OrderID: int = 0 with get, set
        member val CustomerID: string = null with get, set
        member val OrderDate: Nullable<DateTime> = Nullable<DateTime>() with get, set
        member val ShippedDate: Nullable<DateTime> = Nullable<DateTime>() with get, set
        member val Freight: Nullable<decimal> = Nullable<decimal>() with get, set
        member val ShipName: string = null with get, set
        member val ShipCity: string = null with get, set
        member val ShipCountry: string = null with get, set
        member val Customer: Customer = null with get, set
        end

type public DataSource () = class
    static let FOLDER = HttpContext.Current.Server.MapPath ("/data")

    static let mutable _Customers: seq<Customer> = null
    static let mutable _Orders: seq<Order> = null

    static let xn = XName.Get

    static do
        Console.WriteLine("... loading {0}\\XCustomers.xml", FOLDER)
        _Customers <- XElement
            .Load(FOLDER + @"\XCustomers.xml")
            .Elements(xn "Customer")
            .Select(fun x ->
                new Customer (
                    CustomerID = x.Element(xn "CustomerID").Value,
                    CompanyName = x.Element(xn "CompanyName").Value,
                    ContactName = x.Element(xn "ContactName").Value))
            .ToArray()

        Console.WriteLine("... loading {0}\\XOrders.xml", FOLDER)
        _Orders <- XElement
            .Load(FOLDER + @"\XOrders.xml")
            .Elements(xn "Order")
            .Select(fun x ->
                new Order (
                    OrderID = Int32.Parse (x.Element(xn "OrderID").Value),
                    CustomerID = x.Element(xn "CustomerID").Value,
                    OrderDate = (if String.IsNullOrEmpty(x.Element(xn "OrderDate").Value) then Nullable<DateTime>() else Nullable (DateTime.Parse (x.Element(xn "OrderDate").Value))),
                    ShippedDate = (if not <| isNull(x.Element(xn "ShippedDate")) then (if String.IsNullOrEmpty(x.Element(xn "ShippedDate").Value) then Nullable<DateTime>() else Nullable (DateTime.Parse (x.Element(xn "ShippedDate").Value))) else Nullable<DateTime>()),
                    Freight = (if not <| isNull(x.Element(xn "Freight")) then (if String.IsNullOrEmpty(x.Element(xn "Freight").Value) then Nullable<decimal>() else Nullable (Decimal.Parse (x.Element(xn "Freight").Value))) else Nullable<decimal>()),
                    ShipName = x.Element(xn "ShipName").Value,
                    ShipCity = x.Element(xn "ShipCity").Value,
                    ShipCountry = x.Element(xn "ShipCountry").Value))
            .ToArray()

        Console.WriteLine("... relating _Customers with _Orders")

        let _orders_lookup = _Orders.ToLookup (fun o -> o.CustomerID)
        let _customers_dict = _Customers.ToDictionary (fun c -> c.CustomerID)
        for o in _Orders do o.Customer <- _customers_dict.[o.CustomerID]
        for c in _Customers do c.Orders <- _orders_lookup.[c.CustomerID]

        Console.WriteLine("... starting");

    member this.Customers
        with get (): IQueryable<Customer> =
            Console.WriteLine("... returning Customers")
            _Customers.AsQueryable()

    member this.Orders
        with get (): IQueryable<Order> =
            Console.WriteLine("... returning Orders")
            _Orders.AsQueryable()
    end

[<ServiceBehavior(IncludeExceptionDetailInFaults = true)>]
type public A4FS () = class
    inherit DataService<DataSource> ()
    static member InitializeService (config: DataServiceConfiguration): unit = 
        config.SetEntitySetAccessRule ("*", EntitySetRights.AllRead)
        config.DataServiceBehavior.MaxProtocolVersion <- DataServiceProtocolVersion.V3;
        config.UseVerboseErrors <- true;
    end