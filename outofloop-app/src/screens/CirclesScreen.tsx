import { useState } from "react";
import { Modal, ScrollView, StyleSheet, Text, View } from "react-native";

import { ActionButton } from "../components/ActionButton";
import { MemberPreview } from "../components/MemberPreview";
import { Pill } from "../components/Pill";
import { SmartHint } from "../components/SmartHint";
import {
  circleMembers,
  circles,
  UpcomingPlan
} from "../data/mockMissions";
import { AppPreferences } from "../data/preferences";
import { colors, radius } from "../theme/colors";

type Circle = (typeof circles)[number];
type PlanTemplate = (typeof planTemplates)[number];

const planTemplates = [
  {
    title: "Cafe curto sem complicar",
    originMission: "Convida alguem para um encontro simples.",
    time: "Hoje, 18:30",
    place: "Cafe perto de todos",
    durationLabel: "leve",
    accessibility: "baixo custo, facil de sair cedo",
    checklist: [
      "Confirmar quem vem",
      "Escolher sitio simples",
      "Nao transformar isto num grande evento"
    ]
  },
  {
    title: "Volta curta para respirar",
    originMission: "Sai da rotina com uma caminhada leve.",
    time: "Amanha, fim de tarde",
    place: "Jardim ou rua calma",
    durationLabel: "realista",
    accessibility: "percurso curto, ritmo calmo",
    checklist: [
      "Combinar ponto de encontro",
      "Avisar se precisares de banco ou pausa",
      "Ir mesmo que sejam so duas pessoas"
    ]
  },
  {
    title: "Conversa a mesa",
    originMission: "Cria uma conversa real em familia ou circulo.",
    time: "Proximo jantar",
    place: "Casa",
    durationLabel: "realista",
    accessibility: "sentado, privado, previsivel",
    checklist: [
      "Escolher uma pergunta",
      "Cada pessoa pode passar",
      "Guardar uma memoria no fim"
    ]
  }
];

export function CirclesScreen({
  preferences,
  onCreatePlan
}: {
  preferences: AppPreferences;
  onCreatePlan: (plan: UpcomingPlan) => void;
}) {
  const [selectedCircle, setSelectedCircle] = useState<Circle | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<PlanTemplate | null>(
    null
  );
  const [safetyCircle, setSafetyCircle] = useState<Circle | null>(null);
  const [mutedCircles, setMutedCircles] = useState<Record<string, string>>({});

  function buildPlan(
    circle: Circle,
    template: PlanTemplate,
    useSmartVersion: boolean
  ): UpcomingPlan {
    const smartTitle = useSmartVersion
      ? `${template.title} - versao leve`
      : template.title;
    const smartTime = useSmartVersion ? "Hoje, janela flexivel" : template.time;
    const smartAccessibility = useSmartVersion
      ? `${template.accessibility}, saida facil`
      : template.accessibility;
    const smartChecklist = useSmartVersion
      ? [
          "Dizer hora e ponto de encontro",
          "Avisar que da para sair cedo",
          "Manter custo e duracao claros"
        ]
      : template.checklist;

    return {
      id: `plan-${circle.id}-${Date.now()}`,
      title: smartTitle,
      circle: circle.name,
      time: smartTime,
      place: template.place,
      costTier: "gratis",
      durationLabel: useSmartVersion ? "leve" : template.durationLabel,
      acceptedCount: 1,
      capacity: circle.type === "Familia" ? 5 : 6,
      deadline: useSmartVersion ? "responder ate ao fim do dia" : "fecha hoje as 21:00",
      accessibility: smartAccessibility,
      host: "Tu",
      originMission: template.originMission,
      safetyNote:
        "Plano criado no circulo: hora, local, custo e conforto ficam claros antes de alguem responder.",
      checklist: smartChecklist,
      attendees: circleMembers[circle.name] ?? []
    };
  }

  function createPlan(
    circle: Circle,
    template: PlanTemplate,
    useSmartVersion = false
  ) {
    onCreatePlan({
      ...buildPlan(circle, template, useSmartVersion)
    });
    setSelectedTemplate(null);
    setSelectedCircle(null);
  }

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.header}>
        <Text style={styles.title}>Os teus circulos</Text>
        <Text style={styles.subtitle}>
          Comunidade privada, pequena e com regras claras.
        </Text>
      </View>

      {circles.map((circle) => (
        <View key={circle.id} style={styles.card}>
          <View style={styles.cardHeader}>
            <View>
              <Text style={styles.cardTitle}>{circle.name}</Text>
              <Text style={styles.meta}>{circle.members} membros</Text>
            </View>
            <Pill tone={circle.role === "Anfitriao" ? "green" : "muted"}>
              {circle.role}
            </Pill>
          </View>
          <Text style={styles.next}>Proximo: {circle.next}</Text>
          {mutedCircles[circle.id] ? (
            <View style={styles.safetySavedBox}>
              <Text style={styles.safetySavedTitle}>Sinal guardado</Text>
              <Text style={styles.safetySavedText}>
                {mutedCircles[circle.id]}
              </Text>
            </View>
          ) : null}
          <View style={styles.visibilityBox}>
            <Text style={styles.visibilityTitle}>Quem ve isto?</Text>
            <Text style={styles.visibilityText}>
              Membros deste circulo podem ver nome, username e localidade
              aproximada, conforme as escolhas de cada pessoa.
            </Text>
          </View>
          <ScrollView
            horizontal
            showsHorizontalScrollIndicator={false}
            contentContainerStyle={styles.membersRow}
          >
            {(circleMembers[circle.name] ?? []).map((member) => (
              <MemberPreview key={member.id} member={member} />
            ))}
          </ScrollView>
          <View style={styles.actions}>
            <ActionButton
              variant="secondary"
              style={styles.actionGrow}
              onPress={() => setSelectedCircle(circle)}
            >
              Criar plano
            </ActionButton>
            <ActionButton variant="ghost" style={styles.actionGrow}>
              Convidar
            </ActionButton>
            <ActionButton
              variant="ghost"
              style={styles.actionGrow}
              onPress={() => setSafetyCircle(circle)}
            >
              Segurança
            </ActionButton>
          </View>
        </View>
      ))}

      <ActionButton>Criar circulo</ActionButton>
      <ActionButton variant="ghost">Saltar grupos por agora</ActionButton>

      <Modal
        animationType="slide"
        transparent
        visible={selectedCircle !== null}
        onRequestClose={() => setSelectedCircle(null)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            {selectedCircle ? (
              <>
                <Text style={styles.modalKicker}>Criar plano simples</Text>
                <Text style={styles.modalTitle}>{selectedCircle.name}</Text>
                <Text style={styles.modalText}>
                  Escolhe um plano simples. Ele aparece em Quem alinha? com
                  hora, local, custo e prazo para responder.
                </Text>
                {planTemplates.map((template) => (
                  <ActionButton
                    key={template.title}
                    variant="secondary"
                    onPress={() => setSelectedTemplate(template)}
                  >
                    {template.title}
                  </ActionButton>
                ))}
                {selectedTemplate ? (
                  <View style={styles.reviewBox}>
                    <Text style={styles.reviewTitle}>
                      Rever antes de criar
                    </Text>
                    <Text style={styles.reviewPlanTitle}>
                      {selectedTemplate.title}
                    </Text>
                    <Text style={styles.reviewText}>
                      {selectedTemplate.time} · {selectedTemplate.place}
                    </Text>
                    {preferences.smartHelp.improveCreatedPlans ? (
                      <SmartHint
                        title="Ajuda inteligente"
                        text="Sugestao: deixar a hora mais flexivel, reforcar que da para sair cedo e manter custo/duracao claros."
                      />
                    ) : null}
                    <ActionButton
                      onPress={() =>
                        createPlan(selectedCircle, selectedTemplate, false)
                      }
                    >
                      Criar este plano
                    </ActionButton>
                    {preferences.smartHelp.improveCreatedPlans ? (
                      <ActionButton
                        variant="secondary"
                        onPress={() =>
                          createPlan(selectedCircle, selectedTemplate, true)
                        }
                      >
                        Criar versao mais leve
                      </ActionButton>
                    ) : null}
                  </View>
                ) : null}
                <ActionButton
                  variant="ghost"
                  onPress={() => {
                    setSelectedTemplate(null);
                    setSelectedCircle(null);
                  }}
                >
                  Voltar
                </ActionButton>
              </>
            ) : null}
          </View>
        </View>
      </Modal>

      <Modal
        animationType="slide"
        transparent
        visible={safetyCircle !== null}
        onRequestClose={() => setSafetyCircle(null)}
      >
        <View style={styles.modalBackdrop}>
          <View style={styles.modalCard}>
            {safetyCircle ? (
              <>
                <Text style={styles.modalKicker}>Segurança do circulo</Text>
                <Text style={styles.modalTitle}>{safetyCircle.name}</Text>
                <Text style={styles.modalText}>
                  Se algo te deixa desconfortavel, podes reduzir contacto,
                  esconder convites ou enviar um sinal. Isto deve ser privado.
                </Text>
                <ActionButton
                  variant="secondary"
                  onPress={() => {
                    setMutedCircles((current) => ({
                      ...current,
                      [safetyCircle.id]:
                        "Convites deste circulo ficam menos presentes para ti."
                    }));
                    setSafetyCircle(null);
                  }}
                >
                  Receber menos convites
                </ActionButton>
                <ActionButton
                  variant="secondary"
                  onPress={() => {
                    setMutedCircles((current) => ({
                      ...current,
                      [safetyCircle.id]:
                        "Sinal de seguranca guardado. Depois ligamos isto a moderacao."
                    }));
                    setSafetyCircle(null);
                  }}
                >
                  Enviar sinal de seguranca
                </ActionButton>
                <ActionButton
                  variant="ghost"
                  onPress={() => setSafetyCircle(null)}
                >
                  Voltar
                </ActionButton>
              </>
            ) : null}
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: {
    padding: 20,
    gap: 14
  },
  header: {
    gap: 8,
    marginBottom: 4
  },
  title: {
    color: colors.ink,
    fontSize: 32,
    fontWeight: "900",
    letterSpacing: 0
  },
  subtitle: {
    color: colors.inkMuted,
    fontSize: 16,
    lineHeight: 23,
    letterSpacing: 0
  },
  card: {
    backgroundColor: colors.surface,
    borderRadius: radius.lg,
    padding: 16,
    gap: 14,
    borderWidth: 1,
    borderColor: colors.line
  },
  cardHeader: {
    flexDirection: "row",
    justifyContent: "space-between",
    gap: 12
  },
  cardTitle: {
    color: colors.ink,
    fontSize: 20,
    fontWeight: "900",
    letterSpacing: 0
  },
  meta: {
    color: colors.inkMuted,
    fontSize: 13,
    letterSpacing: 0
  },
  next: {
    color: colors.ink,
    fontSize: 15,
    lineHeight: 21,
    letterSpacing: 0
  },
  visibilityBox: {
    backgroundColor: colors.greenSoft,
    borderRadius: radius.sm,
    padding: 12,
    gap: 5
  },
  visibilityTitle: {
    color: colors.green,
    fontSize: 14,
    fontWeight: "900",
    letterSpacing: 0
  },
  visibilityText: {
    color: colors.ink,
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0
  },
  safetySavedBox: {
    backgroundColor: colors.coralSoft,
    borderRadius: radius.sm,
    padding: 12,
    gap: 5
  },
  safetySavedTitle: {
    color: colors.coral,
    fontSize: 14,
    fontWeight: "900",
    letterSpacing: 0
  },
  safetySavedText: {
    color: colors.ink,
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0
  },
  reviewBox: {
    backgroundColor: colors.surface,
    borderRadius: radius.sm,
    padding: 12,
    gap: 10,
    borderWidth: 1,
    borderColor: colors.line
  },
  reviewTitle: {
    color: colors.coral,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  reviewPlanTitle: {
    color: colors.ink,
    fontSize: 18,
    lineHeight: 22,
    fontWeight: "900",
    letterSpacing: 0
  },
  reviewText: {
    color: colors.inkMuted,
    fontSize: 14,
    lineHeight: 20,
    letterSpacing: 0
  },
  membersRow: {
    gap: 9,
    paddingRight: 4
  },
  actions: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 10
  },
  actionGrow: {
    flex: 1
  },
  modalBackdrop: {
    flex: 1,
    justifyContent: "flex-end",
    backgroundColor: "rgba(31, 39, 35, 0.42)"
  },
  modalCard: {
    backgroundColor: colors.background,
    borderTopLeftRadius: radius.lg,
    borderTopRightRadius: radius.lg,
    padding: 20,
    paddingBottom: 30,
    gap: 12
  },
  modalKicker: {
    color: colors.coral,
    fontSize: 13,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  modalTitle: {
    color: colors.ink,
    fontSize: 28,
    lineHeight: 32,
    fontWeight: "900",
    letterSpacing: 0
  },
  modalText: {
    color: colors.inkMuted,
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
  }
});
