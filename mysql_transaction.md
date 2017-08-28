## Mysql Transaction

#### Conditions

- Mysql version: 5.5.5
- Isolation mode: `REPEATABLE-READ`(default in MariaDB)
    ```mysql
    SELECT @@GLOBAL.tx_isolation, @@tx_isolation;
    SET SESSION TRANSACTION ISOLATION LEVEL REPEATABLE READ;
    ```
- Test table:

    ```mysql
    CREATE TABLE `a` (
      `b` varchar(20) NOT NULL,
      `c` char(10) NOT NULL,
      `d` mediumtext NOT NULL,
      UNIQUE KEY `index_a` (`b`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8
    ```

- Data:

    ```mysql
    SELECT * FROM a;
    ```
    | b  | c  | d  |
    |----|----|----|
    | m1 | m2 | m3 |
    | n1 | n2 | n3 |

#### Cases

- ```for update``` only valid inside transaction

    | session A  | session B  | Result  | Comment |
    |------------|------------|---------|---------|
    | COMMIT; | COMMIT; | `OK` | End previous transactions |
    | SELECT * FROM a FOR UPDATE; | - | `OK` | A try to lock |
    | - | SELECT * FROM a FOR UPDATE; | `OK` | Expect to wait since it locked by A, but not  |
    | - | UPDATE a SET c='m4' WHERE b='m1';| `OK` | Expect to wait since it locked by A, but not  |

-
