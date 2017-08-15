### phpunit

Version: 4.0.20

- `bootstrap/autoload.php` only loaded once for each phpunit run(specified in `phpunit.xml`)
    1. Models’ static attributes will be shared among different test classes&functions
- `Testcase.php->createApplication()` is called before every test function run
    1. `require bootstrap_start_test.php` called before every test function run
        1. new Laravel app (`Illuminate\Foundation\Application`) for each test function run
