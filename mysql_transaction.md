# Mysql Transaction

### Conditions

- Mysql version: 5.5.5
- Engine: InnoDB
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

### Cases

- #### ```for update``` only valid inside transaction

    | session A  | session B  | Result  | Comment |
    |------------|------------|---------|---------|
    | ```COMMIT;``` | ```COMMIT;``` | `OK` | End previous transactions |
    | ```SELECT * FROM a FOR UPDATE;``` | | `OK` | A try to lock |
    | | ```SELECT * FROM a FOR UPDATE;``` | `OK` | Expect to wait since it locked by A, but not  |
    | | ```UPDATE a SET c='c4' WHERE b='m1';```| `OK` | Expect to wait since it locked by A, but not  |

- #### With using `index`: ```for update``` only lock the **corresponding rows**

    | session A  | session B  | Result  | Comment |
    |------------|------------|---------|---------|
    | ```COMMIT;``` | ```COMMIT;``` | `OK` | End previous transactions |
    | ```START TRANSACTION;```| |`OK`| |
    | ```SELECT * FROM a WHERE b='m1' FOR UPDATE;```| |`OK`|Lock the first row|
    | | ```UPDATE a SET c='c0' WHERE b='m1';```|`TIMEOUT`|Locked as expected|
    | | ```UPDATE a SET c='c1' WHERE b='n1';```|`OK`|Other rows is free|
    | | ```UPDATE a SET c='c2' WHERE 1;```|`TIMEOUT`|Locked as expected|

- #### Without using `index`: ```for update``` will lock the **whole table**

    - example 1(no index)

        ```mysql
        ALTER TABLE a DROP INDEX index_a;
        ```
        | session A  | session B  | Result  | Comment |
        |------------|------------|---------|---------|
        | ```COMMIT;``` | ```COMMIT;``` | `OK` | End previous transactions |
        | ```START TRANSACTION;```| |`OK`| |
        | ```SELECT * FROM a WHERE b='m1' FOR UPDATE;```| |`OK`|Lock the first row|
        | | ```UPDATE a SET c='c1' WHERE b='n1';```|`TIMEOUT`|Other rows also locked|

    - example 2:has index but not used: `b LIKE "%sth%"`

        ```mysql
        ALTER TABLE a ADD INDEX index_a(b);
        ```
        | session A  | session B  | Result  | Comment |
        |------------|------------|---------|---------|
        | ```COMMIT;``` | ```COMMIT;``` | `OK` | End previous transactions |
        | ```START TRANSACTION;```|-|`OK`| |
        | ```SELECT * FROM a WHERE b LIKE "%m1%" FOR UPDATE;```|-|`OK`|Lock the first row|
        | | ```UPDATE a SET c='c1' WHERE b='n1';```|`TIMEOUT`|Other rows also locked|

    - example 3: has index but not used: `b=1234` in transaction

        | session A  | session B  | Result  | Comment |
        |------------|------------|---------|---------|
        | ```COMMIT;``` | ```COMMIT;``` | `OK` | End previous transactions |
        | ```START TRANSACTION;```| |`OK`| |
        | ```SELECT * FROM a WHERE b=1234 FOR UPDATE;```| |`OK`|Lock the first row|
        | | ```UPDATE a SET c='c1' WHERE b='n1';```|`TIMEOUT`|Other rows also locked|

    - example 4: Also be careful for the coming update

        | session A  | session B  | Result  | Comment |
        |------------|------------|---------|---------|
        | ```COMMIT;``` | ```COMMIT;``` | `OK` | End previous transactions |
        | ```START TRANSACTION;```| |`OK`| |
        | ```SELECT * FROM a WHERE b='m1' FOR UPDATE;```| |`OK`|Lock the first row|
        | | ```UPDATE a SET c='c1' WHERE b=11;```|`TIMEOUT`|Other rows also locked|


