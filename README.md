# kindergarten-reservation
Kindergarten reservation system

Django application

## What is does

System enables to manage presense of childern in kindergarden as well as plan
kindergarden capacity for each month.

There are two user types:

1. Teacher - needs to see capacity for each day, mark child as present, handle
   irregular changes. Teacher also needs to see list of childer, their parents
   and contact details.

2. Parent - needs to see, how many times his childern were missing, use
   potentially available slots for next days, have overview of missed days


## How to use the software

This is Django application - standalone project. You need to

1. adjust your settings (`from settings.base import *` and continue changing)
2. if used along with other django apps, needs to be add to `INSTALLED_APPS`

## How to the release process works

When ever I sleep well and feel the urge, I may commit into master branch.

## How the dependencies that the software has

Just Django. Bootstrap is used as external lib.

## Legaly usage of the software

See the `LICENSE.md` file - this is open source software using MIT license.

## Contribution

Just use GitHub pull requests, drop me an e-mail.
