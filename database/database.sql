CREATE TABLE Expenses (
  id int NOT NULL,
  type varchar(255) NOT NULL,
  name varchar(255) NOT NULL,
  value numeric(10, 2) NOT NULL, 
  date date NOT NULL,
  installments bool NOT NULL DEFAULT FALSE,
  installments_months varchar[],
  CONSTRAINT PK_Expenses PRIMARY KEY(id)
)
