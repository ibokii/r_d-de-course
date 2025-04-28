/*
 Завдання на SQL до лекції 03.
 */

/*
1.
Вивести кількість фільмів в кожній категорії.
Результат відсортувати за спаданням.
*/

SELECT 
	c.name AS "Category Name", 
	COUNT(f.film_id) AS "Film Count"
FROM film_category fc 
INNER JOIN film f 
	ON f.film_id = fc.film_id
INNER JOIN category c 
	ON c.category_id = fc.category_id
GROUP BY c."name"
ORDER BY "Film Count" DESC;

/*
2.
Вивести 10 акторів, чиї фільми брали на прокат найбільше.
Результат відсортувати за спаданням.
*/

SELECT a.first_name || ' ' || a.last_name AS "Actor"
FROM actor a 
INNER JOIN film_actor fa 
	ON fa.actor_id = a.actor_id
INNER JOIN film f 
	ON f.film_id = fa.film_id
INNER JOIN inventory i 
	ON i.film_id = f.film_id
INNER JOIN rental r 
	ON r.inventory_id  = i.inventory_id
GROUP BY a.actor_id
ORDER BY COUNT(r.rental_id) DESC
LIMIT 10;

/*
3.
Вивести категорію фільмів, на яку було витрачено найбільше грошей
в прокаті
*/

REFRESH MATERIALIZED VIEW rental_by_category;

SELECT category AS "Category Name"
FROM rental_by_category
LIMIT 1;

/*
Або
*/

SELECT category AS "Category Name"
FROM sales_by_film_category
LIMIT 1;

/*
Або (хоч і не вбачаю сенсу, переписувати, що вже є готове)
*/

SELECT c.name AS "Category Name"
FROM category c
INNER JOIN film_category fc 
	ON c.category_id = fc.category_id
INNER JOIN film f 
	ON f.film_id = fc.film_id
INNER JOIN inventory i 
	ON i.film_id = f.film_id
INNER JOIN rental r 
	ON r.inventory_id = i.inventory_id
INNER JOIN payment p 
	ON p.rental_id = r.rental_id
GROUP BY c.category_id
ORDER BY (SUM(p.amount)) DESC
LIMIT 1;

/*
4.
Вивести назви фільмів, яких не має в inventory.
Запит має бути без оператора IN
*/

SELECT f.title
FROM film f
LEFT JOIN inventory i 
	ON f.film_id = i.film_id
WHERE i.film_id IS NULL;

/*
5.
Вивести топ 3 актори, які найбільше зʼявлялись в категорії фільмів “Children”.
*/

SELECT a.first_name || ' ' || a.last_name AS "Actor", COUNT(f.film_id) AS "Appearance Count"
FROM actor a 
INNER JOIN film_actor fa 
	ON fa.actor_id = a.actor_id
INNER JOIN film f 
	ON f.film_id = fa.film_id
INNER JOIN film_category fc 
	ON fc.film_id = f.film_id
INNER JOIN category c 
	ON c.category_id = fc.category_id
WHERE c.name = 'Children'
GROUP BY a.first_name, a.last_name
ORDER BY COUNT(f.film_id) DESC
LIMIT 3;
