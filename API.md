# Flask
```
#Cerebro
Route = /api/criar/agendamento
HTTP = POST
return = verifica no banco de dados e retorna se há conflito de horário (200 ou 409)
```

```
Route = /api/criar/cientista
HTTP = PUT
return = status de sucesso
```

```
Route = api/time
HTTP = GET
return = dateTime
```


# NODE JS
```
#Porteiro
Route = /api/request/agendamento
HTTP = POST
return = Retorna log e estado (200 ou 409)
    lock() -> se 200
    unlock() -> se cientista conclui agendamento
```