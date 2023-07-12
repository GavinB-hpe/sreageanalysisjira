# TODO and known issues

## Known issues

### Priority mixup
The priority is not being set as a string but as an object AND the priority name is not Critical, High, Medium, Low etc but
Critical, P2, P3 etc. for some reason.

Need to extract the priority name and use that rather than object, and deal with the odd names