# Nightmare Customer

**Point: 51**

You stumble upon the infamous online tech shop called "Cosmic Components Co." Their entire business model seems designed to rip off individual customers while raking in billions and billions of dollars from deals with AI Data Centers.

Exploit their website and buy all the products to show them that the regular costumer shouldn't be neglected!

The core bug is **persistent coupon stacking**.

- Endpoints:
  - `POST /cart/add`
  - `POST /cart/coupon`
  - `POST /cart/remove`
- Coupons `NEWCUSTOMER10` and `SPACESALE15` are intended for Product 1, but their discount effect can remain active after Product 1 is removed.
- Repeating this loop increases effective discount globally:
  1. Add Product 1
  2. Apply both coupons
  3. Remove Product 1

Tier progression (`/wallet-ledger`) depends on purchases:
`Rookie -> Silver -> Gold -> Platinum -> Diamond -> Elite`.

The `/flag` route is blocked until **Elite** status, so the exploit goal is:

1. Stack discounts with Product 1 loop until items are affordable.
2. Buy products in progression-friendly order: **1 -> 2 -> 6 -> 3 -> 4 -> 5**.
3. Reach Elite and complete buy-all-products condition.
4. Open `/flag`.

## Flag

`UVT{sp4c3_sh0pp3r_3xtr40rd1n41r3_2026}`
