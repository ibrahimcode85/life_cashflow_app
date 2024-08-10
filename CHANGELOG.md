# Changelog

## v1.0.0-beta

### Added or Changed

- Initial pre-release preview. Please refer to readme file for more information.

## v1.0.1-beta (not release yet)

- Docsting added for better documentation
- Fix the lapse rate lookup. The lapse rate should equal to 100% only when it reach the final policy month not the final policy year (otherwise we will see 12 monthsof 100% rate )
- Rearrange the module so that the calculation of decrements will occur after per-policy cashflows calculation, but before inforce cashflows calc. The reason is that the lapse rate is made dependent on the unit fund being non-zero, otherwise it will be lapsed (i.e lapse due to insufficient fund)
