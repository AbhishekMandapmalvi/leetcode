SELECT e.name, b.bonus
FROM Employee AS e LEFT OUTER JOIN Bonus AS b
ON e.empId = b.empId
WHERE b.bonus is NULL OR b.bonus < 1000