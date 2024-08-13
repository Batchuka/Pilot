# Configuração de Docker Remoto para Deploy

Para realizar o deploy utilizando Docker remoto, é necessário configurar o serviço Docker (Daemon) na máquina alvo — que certamente é uma máquina remota e não o seu desktop. Geralmente, essa máquina remota terá o docker rodando com a porta 2375 liberada, para que outros docker consigam se comunicar com o docker dessa máquina.

### Considerações de Segurança

É importante notar que o Docker não implementa TLS default, isto é, não há certificação e criptografia nos pacotes direcionados à porta 2375 do Docker, [leia isso](https://docs.docker.com/engine/daemon/remote-access/). Assim sendo,  você liberar essa porta nas configurações do seu docker, abrirá uma vulnerabilidade que pode ser explorada.

Uma forma de resolver o problema é fazer a máquina remota dropar os pacotes de IP's desconhecidos. Assim, você pode configurar o 'firewall de aplicação' da máquina para somente aceitar os IP's que você sabe que são as máquinas confiáveis. Ainda assim, uma máquina poderia se passar por outra, então não é o jeito ideal. O melhor é correr atrás de configurar o TLS seu preguiçoso.

Caso tenha feito do jeito mal educado, acesse a máquina remota com SSH e busque saber sobre o 'iptables' dela, onde verá as regras relacionadas ao `INPUT`

### Sobre o Docker `context`

Dita as considerações sobre segurança, o docker `context` é uma feature que te permitirá controlar outro docker remoto. Basicamente você consegue configurar um contexto no seu docker que, se caso esteje em uso — `docker context use` — fará com que *qualquer* comondo docker valha para essa máquina remota. Ou seja, ao invés de executar na sua, executará na remota através de conexão socket tcp.

Daí, o pipeline desse utilitário, usa essa feature para automatizar o deploy por esse método. E ele parte do pressuposto que você configurou um docker context, que você pode descobrir como fazer [aqui](https://docs.docker.com/engine/manage-resources/contexts/#create-a-new-context).

Criado, você deve informar o contexto no `.conf` para que ele valide isso antes de começar a executar os comandos. Ele só fará isso, sempre validará se o contexto em que os comandos devem ser executados é o seu atual.

&nbsp;&nbsp;&nbsp;