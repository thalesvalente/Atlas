# Reproduzir a verificação de P01

No checkout da candidata, Python 3 disponível, sem rede/modelo/produtor:

```bash
python -B docs/contracts/atlas-parity-02/p01/validate_examples.py --suite
```

O comando deve retornar exit 0 apenas se todos os exemplos positivos forem aceitos,
todos os negativos retornarem os códigos especificados e as provas do leitor público
preservarem entidades, menções e identidade contextual. Um exemplo individual inválido
retorna exit 1, por exemplo:

```bash
python -B docs/contracts/atlas-parity-02/p01/validate_examples.py --file docs/contracts/atlas-parity-02/p01/examples/negative-mention-as-input.json
```

Helper Spec Kit sem modificar ponteiro:

```bash
SPECIFY_FEATURE_DIRECTORY=specs/004-atlas-parity-c0/workstreams/p01-contracts SPECIFY_FEATURE_NO_PERSIST=1 python -B .specify/scripts/python/check_prerequisites.py --json --require-spec --require-tasks --include-tasks
```

Manifesto a partir da raiz do repositório:

```bash
sha256sum -c docs/missions/atlas-parity-02/p01-contracts/MANIFEST.sha256
```

A revisão final também confere `git diff --name-only BASE...HEAD`: somente as três
raízes P01. A leitura/validação de exemplos não inicia servidor nem abre o navegador.
Os resultados reais e ambientes estão em RESULT/HANDOFF; este guia não é recibo de PASS.
