# Livro de Reclamações para o Mundo - Auditoria Editorial

## Objetivo da nova edição

Criar uma versão mais limpa, forte e profissional para Amazon KDP, mantendo o tom original: crónica irónica, crítica social, absurdo quotidiano e voz direta.

## Diagnóstico

- O ficheiro original `book_1.docx` é a melhor fonte. O EPUB antigo mantém problemas de conversão.
- A extração por XML colava frases, mas a extração por `textutil` preserva as quebras reais. A nova edição deve partir de `livro-reclamacoes-source-textutil.txt`.
- O livro tem 34 reclamações. O conjunto é forte, mas algumas repetem a mesma crítica em torno de algoritmo, solidão, mercado, ego, KPI e performance.
- A nova versão deve respirar melhor: partes em página própria, reclamações sempre em página nova, hierarquia clara entre título, subtítulo, secções internas e corpo.

## Candidatos a corte ou fusão

### Cortar ou fundir com prioridade alta

1. `A Maquilhagem do Óbvio (O Gourmet da Banalidade)`
   - Motivo: repete a crítica ao consumo estetizado e à venda de banalidade. Parte do efeito já aparece em `Consumismo Disfarçado`, `Gurus da Alma e da Carteira` e `A Indústria da Beleza Impossível`.
   - Decisão sugerida: cortar da edição final.

2. `Celebridades Anónimas`
   - Motivo: boa ideia, mas muito próxima de `O Paradoxo da Conectividade` e `O Algoritmo Não Te Ama`.
   - Decisão sugerida: cortar ou aproveitar 1-2 imagens fortes dentro de `O Algoritmo Não Te Ama`.

3. `O Teatro da Presença (O Networking do Isolamento)`
   - Motivo: sobrepõe-se a `Amizades de Conveniência`, `A Liturgia do Calendário Cheio` e `O Evangelho do KPI`.
   - Decisão sugerida: cortar, mantendo `Amizades de Conveniência` como crítica mais humana e mais forte.

4. `Ocupação e Pais (A Terceirização do Afeto)`
   - Motivo: muito próxima de `A Ditadura da Melhor Versão`, sobretudo na crítica à performance familiar e à infância transformada em KPI.
   - Decisão sugerida: fundir as melhores ideias em `A Ditadura da Melhor Versão` ou cortar.

### Reescrever com cuidado

5. `O Manual Infinito do Ser (A Confusão dos Géneros)`
   - Motivo: o tema pode soar mais reativo do que observacional. Para não prejudicar o livro, deve ser reescrito como crítica à burocratização da linguagem e ao medo de conversar, não como ataque a identidades.
   - Decisão sugerida: manter, mas mudar o foco e suavizar o título.

6. `A Ditadura do Ofendidinho`
   - Motivo: título forte, mas pode parecer genérico ou provocatório demais. O conteúdo deve focar cultura de reação, vigilância moral e medo de falar.
   - Decisão sugerida: manter, mas polir título/corpo.

## Estrutura final sugerida

Versão final com cerca de 30 reclamações:

- Manter as Partes I-V.
- Remover 4 reclamações repetitivas.
- Renumerar automaticamente as reclamações.
- Atualizar índice e prefácio para refletir o novo número.

## Regras de edição

- Preservar a voz do autor.
- Corrigir espaços, pontuação e quebras estranhas.
- Reduzir repetições de fórmulas quando aparecem demasiado próximas.
- Evitar excesso de frases como `É a solidão de perceber...` quando usadas em sequência.
- Manter a estrutura recorrente quando ela serve a identidade do livro, mas variar o ritmo para não parecer mecânico.
- Cada reclamação começa em página nova.
- Cada parte começa em página própria.
