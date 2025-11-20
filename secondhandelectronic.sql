CREATE DATABASE ElectronicsStore;
USE ElectronicsStore;
-- ================================================================
-- 2 TABLE CREATION
-- ================================================================
-- Product Model Table
CREATE TABLE ProductModel (
    Product_model_ID INT PRIMARY KEY,
    Model_name VARCHAR(100),
    Brand VARCHAR(50),
    Warranty_Period INT
);

-- Store Table
CREATE TABLE Store (
    Store_ID INT PRIMARY KEY,
    Store_name VARCHAR(100),
    Location VARCHAR(100)
);
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role ENUM('customer','staff') DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
-- Item Table
CREATE TABLE Item (
    Item_ID INT PRIMARY KEY,
    Price DECIMAL(10,2),
    Cond VARCHAR(50),
    Status VARCHAR(50),
    Category VARCHAR(50),
    Quantity_Avl INT,
    Brand_Name VARCHAR(50),
    Product_model_ID INT,
    Store_ID INT,
    FOREIGN KEY (Product_model_ID) REFERENCES ProductModel(Product_model_ID),
    FOREIGN KEY (Store_ID) REFERENCES Store(Store_ID)
);




-- Staff Table
CREATE TABLE Staff (
    Staff_ID INT PRIMARY KEY AUTO_INCREMENT,

    user_id INT UNIQUE NULL,
    Name VARCHAR(100),
    Role VARCHAR(50),
    Contact VARCHAR(50),
    Store_ID INT,
    FOREIGN KEY (Store_ID) REFERENCES Store(Store_ID)
);

-- Customer Table
CREATE TABLE Customer (
    Customer_ID INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT UNIQUE NULL,
    Name VARCHAR(100),
    Address VARCHAR(200)
);

-- CustomerPhone Table
CREATE TABLE CustomerPhone (
    Customer_ID INT,
    Phone_number VARCHAR(20),
    PRIMARY KEY (Customer_ID, Phone_number),
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
);

-- Order Table
CREATE TABLE Orders (
    OrderID INT PRIMARY KEY,
    Date DATE,
    Status VARCHAR(50),
    CustomerID INT,
    FOREIGN KEY (CustomerID) REFERENCES Customer(Customer_ID)
);

-- Payment Table
CREATE TABLE Payment (
    Payment_ID INT PRIMARY KEY,
    Amount DECIMAL(10,2),
    Method VARCHAR(50),
    OrderID INT,
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID)
);

-- Repair Table
CREATE TABLE Repair (
    RepairID INT PRIMARY KEY,
    Issue VARCHAR(200),
    RepairCost DECIMAL(10,2),
    Status VARCHAR(50),
    ItemID INT,
    Staff_ID INT,
    FOREIGN KEY (ItemID) REFERENCES Item(Item_ID),
    FOREIGN KEY (Staff_ID) REFERENCES Staff(Staff_ID)
);

-- Keeps (many-to-many relation between Store & Item)
CREATE TABLE Keeps (
    StoreID INT,
    ItemID INT,
    PRIMARY KEY (StoreID, ItemID),
    FOREIGN KEY (StoreID) REFERENCES Store(Store_ID),
    FOREIGN KEY (ItemID) REFERENCES Item(Item_ID)
);

-- Info (relation between Customer & Item)
CREATE TABLE Info (
    CustomerID INT,
    ItemID INT,
    PRIMARY KEY (CustomerID, ItemID),
    FOREIGN KEY (CustomerID) REFERENCES Customer(Customer_ID),
    FOREIGN KEY (ItemID) REFERENCES Item(Item_ID)
);

-- Contains (relation between Order & Item)
CREATE TABLE Contains (
    OrderID INT,
    ItemID INT,
    Qty INT,
    PRIMARY KEY (OrderID, ItemID),
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID),
    FOREIGN KEY (ItemID) REFERENCES Item(Item_ID)
);

-- RequestRepair (relation between Customer & Repair)
CREATE TABLE RequestRepair (
    CustomerID INT,
    RepairID INT,
    PRIMARY KEY (CustomerID, RepairID),
    FOREIGN KEY (CustomerID) REFERENCES Customer(Customer_ID),
    FOREIGN KEY (RepairID) REFERENCES Repair(RepairID)
);
CREATE TABLE CustomerSell (
    CustomerID INT,
    Product_model_ID INT,            -- Product type they want to sell
    ItemDescription VARCHAR(200),    -- Optional details about the item
    SellDate DATE,
    SellPrice DECIMAL(10,2),
    Status VARCHAR(20) DEFAULT 'Pending',  -- Pending, Accepted, Rejected
    PRIMARY KEY (CustomerID, Product_model_ID, SellDate),
    FOREIGN KEY (CustomerID) REFERENCES Customer(Customer_ID),
    FOREIGN KEY (Product_model_ID) REFERENCES ProductModel(Product_model_ID)
);
Alter commands:
-- Add CHECK constraint to ensure Price is non-negative
ALTER TABLE Item 
ADD CONSTRAINT chk_price CHECK (Price >= 0);

-- Add CHECK constraint for valid warranty period range (0–36 months)
ALTER TABLE ProductModel 
ADD CONSTRAINT chk_warranty CHECK (Warranty_Period BETWEEN 0 AND 36);

-- Modify 'Cond' column in Item table to restrict condition values
ALTER TABLE Item 
MODIFY Cond ENUM('Fair', 'Good', 'Like New', 'Refurbished', 'Excellent') DEFAULT 'Good';

ALTER TABLE CustomerSell
MODIFY Status ENUM('Pending', 'Accepted', 'Rejected','Added to Inventory') DEFAULT 'Pending';

-- =========================
-- Add CASCADE to Item table
-- =========================
ALTER TABLE Item
  DROP FOREIGN KEY Item_ibfk_1,
  ADD CONSTRAINT fk_Item_ProductModel
    FOREIGN KEY (Product_model_ID) REFERENCES ProductModel(Product_model_ID)
    ON DELETE CASCADE ON UPDATE CASCADE;

ALTER TABLE Item
  DROP FOREIGN KEY Item_ibfk_2,
  ADD CONSTRAINT fk_Item_Store
    FOREIGN KEY (Store_ID) REFERENCES Store(Store_ID)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- =========================
-- Add CASCADE to Staff table
-- =========================
ALTER TABLE Staff
  DROP FOREIGN KEY Staff_ibfk_1,
  ADD CONSTRAINT fk_Staff_Store
    FOREIGN KEY (Store_ID) REFERENCES Store(Store_ID)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- =========================
-- Add CASCADE to CustomerPhone table
-- =========================
ALTER TABLE CustomerPhone
  DROP FOREIGN KEY CustomerPhone_ibfk_1,
  ADD CONSTRAINT fk_CustomerPhone_Customer
    FOREIGN KEY (Customer_ID) REFERENCES Customer(Customer_ID)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- =========================
-- Add CASCADE to Orders table
-- =========================
ALTER TABLE Orders
  DROP FOREIGN KEY Orders_ibfk_1,
  ADD CONSTRAINT fk_Orders_Customer
    FOREIGN KEY (CustomerID) REFERENCES Customer(Customer_ID)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- =========================
-- Add CASCADE to Payment table
-- =========================
ALTER TABLE Payment
  DROP FOREIGN KEY Payment_ibfk_1,
  ADD CONSTRAINT fk_Payment_Order
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- =========================
-- Add CASCADE to Repair table
-- =========================
ALTER TABLE Repair
  DROP FOREIGN KEY Repair_ibfk_1,
  DROP FOREIGN KEY Repair_ibfk_2,
  ADD CONSTRAINT fk_Repair_Item
    FOREIGN KEY (ItemID) REFERENCES Item(Item_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT fk_Repair_Staff
    FOREIGN KEY (Staff_ID) REFERENCES Staff(Staff_ID)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- =========================
-- Add CASCADE to Keeps table
-- =========================
ALTER TABLE Keeps
  DROP FOREIGN KEY Keeps_ibfk_1,
  DROP FOREIGN KEY Keeps_ibfk_2,
  ADD CONSTRAINT fk_Keeps_Store
    FOREIGN KEY (StoreID) REFERENCES Store(Store_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT fk_Keeps_Item
    FOREIGN KEY (ItemID) REFERENCES Item(Item_ID)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- =========================
-- Add CASCADE to Info table
-- =========================
ALTER TABLE Info
  DROP FOREIGN KEY Info_ibfk_1,
  DROP FOREIGN KEY Info_ibfk_2,
  ADD CONSTRAINT fk_Info_Customer
    FOREIGN KEY (CustomerID) REFERENCES Customer(Customer_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT fk_Info_Item
    FOREIGN KEY (ItemID) REFERENCES Item(Item_ID)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- =========================
-- Add CASCADE to Contains table
-- =========================
ALTER TABLE Contains
  DROP FOREIGN KEY Contains_ibfk_1,
  DROP FOREIGN KEY Contains_ibfk_2,
  ADD CONSTRAINT fk_Contains_Order
    FOREIGN KEY (OrderID) REFERENCES Orders(OrderID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT fk_Contains_Item
    FOREIGN KEY (ItemID) REFERENCES Item(Item_ID)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- =========================
-- Add CASCADE to RequestRepair table
-- =========================
ALTER TABLE RequestRepair
  DROP FOREIGN KEY RequestRepair_ibfk_1,
  DROP FOREIGN KEY RequestRepair_ibfk_2,
  ADD CONSTRAINT fk_RequestRepair_Customer
    FOREIGN KEY (CustomerID) REFERENCES Customer(Customer_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT fk_RequestRepair_Repair
    FOREIGN KEY (RepairID) REFERENCES Repair(RepairID)
    ON DELETE CASCADE ON UPDATE CASCADE;

-- ================================
-- Add CASCADE to CustomerSell table
-- ================================
ALTER TABLE CustomerSell
  DROP FOREIGN KEY CustomerSell_ibfk_1,
  DROP FOREIGN KEY CustomerSell_ibfk_2,
  ADD CONSTRAINT fk_CustomerSell_Customer
    FOREIGN KEY (CustomerID) REFERENCES Customer(Customer_ID)
    ON DELETE CASCADE ON UPDATE CASCADE,
  ADD CONSTRAINT fk_CustomerSell_ProductModel
    FOREIGN KEY (Product_model_ID) REFERENCES ProductModel(Product_model_ID)
    ON DELETE CASCADE ON UPDATE CASCADE;


-- =============================
-- 1) Product Models
-- =============================
INSERT INTO ProductModel (Product_model_ID, Model_name, Brand, Warranty_Period) VALUES
(1, 'iPhone 12', 'Apple', 6),
(2, 'Dell Inspiron 15', 'Dell', 12),
(3, 'Samsung Galaxy S20', 'Samsung', 6),
(4, 'Sony Bravia 42"', 'Sony', 24),
(5, 'HP Pavilion x360', 'HP', 12),
(6, 'Redmi Note 10', 'Xiaomi', 6);

-- =============================
-- 2) Stores
-- =============================
INSERT INTO Store (Store_ID, Store_name, Location) VALUES
(101, 'Main Branch', 'Bangalore'),
(102, 'City Branch', 'Mysore'),
(103, 'Express Store', 'Chennai');

-- =============================
-- 3) Users
-- =============================
INSERT INTO users (id, name, email, password, role) VALUES
(1, 'Poojitha CV', 'poojitha@example.com', 'pooja123', 'customer'),
(2, 'Sita Sharma', 'sita@example.com', 'sita123', 'staff'),
(3, 'Tester1', 'tester1@example.com', 'abc', 'customer'),
(4, 'tester2', 'tester2@example.com', 'xyz', 'staff');

-- =============================
-- 4) Customers
-- =============================
INSERT INTO Customer (Customer_ID, Name, Address) VALUES
(201, 'Poojitha', 'Bangalore'),
(202, 'Arjun', 'Mysore'),
(203, 'Kavya', 'Chennai'),
(204, 'Rahul', 'Hyderabad'),
(205, 'Sneha', 'Bangalore'),
(206, 'Vikram', 'Mysore'),
(207, 'Ananya', 'Bangalore'),
(208, 'Rohit', 'Mumbai'),
(209, 'Isha', 'Chennai'),
(210, 'Varun', 'Hyderabad');

-- =============================
-- 5) Customer Phones
-- =============================
INSERT INTO CustomerPhone (Customer_ID, Phone_number) VALUES
(201, '9876543210'),
(202, '9123456789'),
(203, '9988776655'),
(204, '9090990909'),
(205, '9666778899'),
(206, '9555112233');

-- =============================
-- 6) Staff
-- =============================
INSERT INTO Staff (Staff_ID, user_id, Name, Role, Contact, Store_ID) VALUES
(301, NULL, 'Ramesh', 'Technician', '9900112233', 101),
(302, NULL, 'Sita', 'Sales', '9877001122', 102),
(303, NULL, 'Kiran', 'Manager', '9788994455', 101),
(304, NULL, 'Meena', 'Technician', '8899776655', 103);

-- =============================
-- 7) Items
-- =============================
INSERT INTO Item (Item_ID, Price, Cond, Status, Category, Quantity_Avl, Brand_Name, Product_model_ID, Store_ID) VALUES
(1001, 35000, 'Good', 'Available', 'Phone', 1, 'Apple', 1, 101),
(1002, 25000, 'Refurbished', 'Available', 'Laptop', 1, 'Dell', 2, 102),
(1003, 20000, 'Like New', 'In Repair', 'Phone', 1, 'Samsung', 3, 101),
(1004, 15000, 'Good', 'Sold', 'TV', 1, 'Sony', 4, 102),
(1005, 42000, 'Excellent', 'Available', 'Laptop', 2, 'HP', 5, 103),
(1006, 12000, 'Fair', 'Available', 'Phone', 1, 'Xiaomi', 6, 103),
(1007, 18000, 'Refurbished', 'Sold', 'Laptop', 1, 'Dell', 2, 101),
(1008, 28000, 'Good', 'Available', 'Laptop', 1, 'HP', 5, 102);

-- =============================
-- 8) Keeps
-- =============================
INSERT INTO Keeps (StoreID, ItemID) VALUES
(101, 1001),(101, 1003),(101, 1007),
(102, 1002),(102, 1004),(102, 1008),
(103, 1005),(103, 1006);

-- =============================
-- 9) Info
-- =============================
INSERT INTO Info (CustomerID, ItemID) VALUES
(201, 1001),(205, 1004),(204, 1005);

-- =============================
-- 10) Orders
-- =============================
INSERT INTO Orders (OrderID, Date, Status, CustomerID) VALUES
(401, '2025-10-01', 'Completed', 201),
(402, '2025-10-02', 'Pending', 202),
(403, '2025-10-03', 'Completed', 205),
(404, '2025-10-04', 'Completed', 204),
(405, '2025-10-05', 'Pending', 206);

-- =============================
-- 11) Contains
-- =============================
INSERT INTO Contains (OrderID, ItemID, Qty) VALUES
(401, 1001, 1),
(402, 1002, 1),
(403, 1004, 1),
(404, 1005, 1),
(405, 1006, 1);

-- =============================
-- 12) Payments
-- =============================
INSERT INTO Payment (Payment_ID, Amount, Method, OrderID) VALUES
(501, 35000, 'Credit Card', 401),
(502, 15000, 'Cash', 403),
(503, 42000, 'UPI', 404);

-- =============================
-- 13) Repairs
-- =============================
INSERT INTO Repair (RepairID, Issue, RepairCost, Status, ItemID, Staff_ID) VALUES
(601, 'Screen Replacement', 5000, 'Completed', 1003, 301),
(602, 'Battery Issue', 1500, 'Pending', 1002, 301),
(603, 'Keyboard Fault', 2000, 'In Progress', 1007, 304),
(604, 'Screen Flicker', 1200, 'Pending', 1001, 301),
(605, 'Motherboard Failure', 8500, 'In Progress', 1003, 304),
(606, 'Touchpad Not Working', 900, 'Pending', 1005, 301),
(607, 'Overheating Issue', 1500, 'In Progress', 1006, 304),
(608, 'Battery Swelling', 5000, 'Pending', 1008, 303),
(609, 'GPU Thermal Throttle', 6500, 'In Progress', 1005, 304),
(610, 'Speaker Crackling', 750, 'Pending', 1006, 302),
(611, 'Boot Loop Issue', 1800, 'In Progress', 1001, 303);

-- =============================
-- 14) RequestRepair
-- =============================
INSERT INTO RequestRepair (CustomerID, RepairID) VALUES
(201, 601),(202, 602),(206, 603);

-- =============================
-- 15) CustomerSell
-- =============================
INSERT INTO CustomerSell (CustomerID, Product_model_ID, ItemDescription, SellDate, SellPrice, Status) VALUES
(201, 1, 'Used iPhone 12, 64GB, minor scratches', '2025-10-07', 28000, 'Accepted'),
(202, 2, 'Old Dell Inspiron 15 laptop, working condition', '2025-10-08', 20000, 'Pending'),
(207, 3, 'Samsung S20, minor scratches', '2025-10-11', 22000, 'Accepted'),
(208, 4, 'Sony TV, used', '2025-10-12', 15000, 'Accepted'),
(209, 5, 'HP Laptop, working', '2025-10-13', 40000, 'Accepted'),
(210, 6, 'Redmi Note 10, good condition', '2025-10-14', 12000, 'Accepted');

-- =============================
--  FUNCTIONS / PROCEDURES / TRIGGERS
-- =============================
DELIMITER $$
CREATE FUNCTION CheckStock(p_ItemID INT)
RETURNS VARCHAR(20)
DETERMINISTIC
BEGIN
    DECLARE qty INT;
    DECLARE result VARCHAR(20);
    SELECT Quantity_Avl INTO qty FROM Item WHERE Item_ID = p_ItemID;
    IF qty > 0 THEN
        SET result = 'Available';
    ELSE
        SET result = 'Out of Stock';
    END IF;
    RETURN result;
END$$
DELIMITER ;


DELIMITER //
CREATE FUNCTION WarrantyExpiry(months INT)
RETURNS DATE
DETERMINISTIC
BEGIN
  RETURN DATE_ADD(CURDATE(), INTERVAL months MONTH);
END;
//
DELIMITER ;

-- Procedure: AddToInventoryFromCustomerSell
-- Purpose  : Add accepted customer-sold items to inventory
DELIMITER $$
CREATE PROCEDURE AddToInventoryFromCustomerSell(
    IN p_CustomerID INT,
    IN p_Product_model_ID INT,
    IN p_StoreID INT
)
BEGIN
    DECLARE v_Item_ID INT;
    DECLARE v_Brand VARCHAR(50);
    DECLARE v_ModelName VARCHAR(100);
    DECLARE v_SellPrice DECIMAL(10,2);
    DECLARE v_Description VARCHAR(200);
    DECLARE v_Status VARCHAR(20);

    -- Step 1: Fetch the sell details
    SELECT cs.SellPrice, cs.ItemDescription, cs.Status, pm.Brand, pm.Model_name
    INTO v_SellPrice, v_Description, v_Status, v_Brand, v_ModelName
    FROM CustomerSell cs
    JOIN ProductModel pm ON cs.Product_model_ID = pm.Product_model_ID
    WHERE cs.CustomerID = p_CustomerID AND cs.Product_model_ID = p_Product_model_ID
    ORDER BY cs.SellDate DESC
    LIMIT 1;

    -- Step 2: If accepted, add to Item and Keeps
    IF v_Status = 'Accepted' THEN
        SELECT IFNULL(MAX(Item_ID), 1000) + 1 INTO v_Item_ID FROM Item;

        INSERT INTO Item (
            Item_ID, Price, Cond, Status, Category, Quantity_Avl, Brand_Name,
            Product_model_ID, Store_ID
        )
        VALUES (
            v_Item_ID, v_SellPrice, 'Good', 'Available', 'Electronics', 1,
            v_Brand, p_Product_model_ID, p_StoreID
        );

        INSERT INTO Keeps (StoreID, ItemID)
        VALUES (p_StoreID, v_Item_ID);

        UPDATE CustomerSell
        SET Status = 'Added to Inventory'
        WHERE CustomerID = p_CustomerID AND Product_model_ID = p_Product_model_ID;

        SELECT CONCAT('✅ Customer item added to inventory with Item_ID = ', v_Item_ID) AS Message;
    ELSE
        SELECT '❌ Item not accepted. Cannot add to inventory.' AS Message;
    END IF;
END $$
DELIMITER ;




/* ================================================================
   🔄 🛒 TRIGGER: REDUCE ITEM QUANTITY ON ORDER
   Automatically decreases Item.Quantity_Avl after a new order
   ================================================================ */
DELIMITER //

-- Reduce Quantity safely
CREATE TRIGGER ReduceQuantity
AFTER INSERT ON Contains
FOR EACH ROW
BEGIN
    DECLARE available INT;
    SELECT Quantity_Avl INTO available FROM Item WHERE Item_ID = NEW.ItemID;
    IF available >= NEW.Qty THEN
        UPDATE Item
        SET Quantity_Avl = Quantity_Avl - NEW.Qty
        WHERE Item_ID = NEW.ItemID;
    ELSE
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Not enough stock to fulfill the order';
    END IF;
END;
//


DELIMITER $$

-- After user insert
CREATE TRIGGER after_user_insert
AFTER INSERT ON users
FOR EACH ROW
BEGIN
    IF NEW.role = 'customer' THEN
        INSERT INTO Customer (user_id, Name) VALUES (NEW.id, NEW.name);
    ELSEIF NEW.role = 'staff' THEN
        INSERT INTO Staff (user_id, Name) VALUES (NEW.id, NEW.name);
    END IF;
END;
//

DELIMITER ;


-- =============================
--  View
-- =============================
CREATE VIEW ItemsInRepair AS
SELECT i.Item_ID, pm.Model_name, r.Issue, r.Status, s.Name AS Technician
FROM Item i
JOIN ProductModel pm ON i.Product_model_ID = pm.Product_model_ID
JOIN Repair r ON i.Item_ID = r.ItemID
JOIN Staff s ON r.Staff_ID = s.Staff_ID
WHERE r.Status != 'Completed';

-- Verify Items In Repair
SELECT * FROM ItemsInRepair;
-- =============================
--  Nested Query
-- =============================
SELECT Name
FROM Customer
WHERE Customer_ID IN (
    SELECT CustomerID
    FROM Orders
    WHERE OrderID IN (
        SELECT OrderID
        FROM Contains
        WHERE ItemID = 1001
    )
);
-- =============================
--  Joins
-- =============================
SELECT c.Name AS CustomerName,
       o.OrderID,
       i.Item_ID,
       i.Brand_Name,
       pm.Model_name,
       ct.Qty,
       o.Status AS OrderStatus
FROM Customer c
JOIN Orders o ON c.Customer_ID = o.CustomerID
JOIN Contains ct ON o.OrderID = ct.OrderID
JOIN Item i ON ct.ItemID = i.Item_ID
LEFT JOIN ProductModel pm ON i.Product_model_ID = pm.Product_model_ID;

-- =============================
-- Aggregate queries
-- =============================

SELECT 
    c.Name AS CustomerName,
    SUM(i.Price * ct.Qty) AS TotalSpent
FROM Customer c
JOIN Orders o ON c.Customer_ID = o.CustomerID
JOIN Contains ct ON o.OrderID = ct.OrderID
JOIN Item i ON ct.ItemID = i.Item_ID
GROUP BY c.Customer_ID, c.Name;

SELECT 
    c.Name AS CustomerName,
    AVG(order_total) AS AvgOrderValue
FROM (
    SELECT 
        o.OrderID,
        o.CustomerID,
        SUM(i.Price * ct.Qty) AS order_total
    FROM Orders o
    JOIN Contains ct ON o.OrderID = ct.OrderID
    JOIN Item i ON ct.ItemID = i.Item_ID
    GROUP BY o.OrderID, o.CustomerID
) AS order_summary
JOIN Customer c ON order_summary.CustomerID = c.Customer_ID
GROUP BY c.Customer_ID, c.Name;

