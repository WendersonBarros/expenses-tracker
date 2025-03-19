CREATE TABLE Expenses (
  ID int NOT NULL,
  Type varchar(255) NOT NULL,
  Name varchar(255) NOT NULL,
  Date date NOT NULL,
  CONSTRAINT PK_Expenses PRIMARY KEY(ID)
)
