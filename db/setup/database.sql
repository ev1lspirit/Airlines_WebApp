CREATE TABLE IF NOT EXISTS Passenger(
   passport integer PRIMARY KEY,
   first_name varchar(40) not null,
   last_name varchar(40) not null,
   birth_date DATE not null,
   phone varchar(15) not null);

CREATE TABLE IF NOT EXISTS User(
   user_id integer PRIMARY KEY,
   username varchar(20) NOT NULL,
   password varchar(100) NOT NULL)

CREATE TABLE IF NOT EXISTS Booking(
   pnr varchar(7) PRIMARY KEY,
   book_date DATE NOT NULL,
   passport integer references Passenger(passport));

CREATE TABLE IF NOT EXISTS City(
    name varchar(40) PRIMARY KEY);

CREATE TABLE IF NOT EXISTS Airport(
    alias varchar(3) PRIMARY KEY,
    city varchar(40) references City(name));

CREATE TABLE IF NOT EXISTS AirplaneModel(
   model varchar(40) PRIMARY KEY,
   manufacturer varchar(40) not null,
   maxdistance integer not null,
   maxaltitude real not null);

CREATE TABLE IF NOT EXISTS CabinType(
   title varchar(15) PRIMARY KEY,
   extraFeeRatio REAL NOT NULL DEFAULT 1,
   SeatsAmount INTEGER NOT NULL);


CREATE TABLE IF NOT EXISTS Airplane(
   boardno integer PRIMARY KEY,
   planemodel varchar(40) references AirplaneModel(model),
   boardname varchar(40));


CREATE TABLE IF NOT EXISTS Flight(
   flightNo integer PRIMARY KEY,
   departureAirport varchar(3) references Airport(alias),
   arrivalAirport varchar(3) references Airport(alias),
   departureDate DATE NOT NULL,
   arrivalDate DATE NOT NULL,
   departureTime TIME NOT NULL,
   arrivalTime TIME NOT NULL,
   airplane integer references Airplane(boardno));

CREATE TABLE IF NOT EXISTS SeatRow(
   rowno integer,
   title varchar(15) references CabinType(title),
   extraFeeRatio REAL NOT NULL DEFAULT 1,
   primary key (rowno, title));

CREATE TABLE IF NOT EXISTS Seat(
   seatno varchar(1),
   title varchar(15),
   rowno integer,
   foreign key (rowno, title) references SeatRow(rowno, title),
   primary key (seatno, rowno, title));

CREATE TABLE IF NOT EXISTS Booking (
  pnr varchar(13) PRIMARY KEY,
  holder_passport integer references Passenger(passport));

CREATE TABLE IF NOT EXISTS Ticket(
  ticketno integer PRIMARY KEY,
  pnr varchar(13) references Booking(pnr),
  seatno varchar(1),
  rowno integer,
  title varchar(15),
  FOREIGN KEY (seatno, rowno, title) references Seat(seatno, rowno, title));


  
  

   

 

 
