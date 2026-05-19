import { useState } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";

import { ActionButton } from "../components/ActionButton";
import { OptionChip } from "../components/OptionChip";
import {
  AppPreferences,
  defaultPreferences
} from "../data/preferences";
import type {
  CostTier,
  MissionIntensity,
  MissionMode
} from "../data/missions.generated";
import { colors, radius } from "../theme/colors";

const modes: Array<{ label: string; value: MissionMode }> = [
  { label: "Social", value: "social" },
  { label: "Recomeço", value: "recomeco" },
  { label: "Coragem", value: "coragem" },
  { label: "Familia", value: "familia" },
  { label: "Saude", value: "saude" }
];

const intensities: Array<{ label: string; value: MissionIntensity }> = [
  { label: "Leve", value: "leve" },
  { label: "Real", value: "real" },
  { label: "Coragem", value: "coragem" }
];

const costs: Array<{ label: string; value: CostTier }> = [
  { label: "Gratis", value: "gratis" },
  { label: "Low cost", value: "low_cost" },
  { label: "Medio", value: "medio" },
  { label: "Especial", value: "especial" }
];

const timeOptions = [
  { label: "Micro", minutes: 5 },
  { label: "Leve", minutes: 15 },
  { label: "Realista", minutes: 30 },
  { label: "Plano", minutes: 60 }
];

const accessibilityOptions = [
  "Locais calmos",
  "Pouca caminhada",
  "Atividade sentada",
  "Plano previsivel",
  "Grupos pequenos"
];

export function OnboardingScreen({
  onComplete
}: {
  onComplete: (preferences: AppPreferences) => void;
}) {
  const [preferences, setPreferences] =
    useState<AppPreferences>(defaultPreferences);

  function toggleAccessibility(value: string) {
    setPreferences((current) => {
      const exists = current.accessibility.includes(value);
      return {
        ...current,
        accessibility: exists
          ? current.accessibility.filter((item) => item !== value)
          : [...current.accessibility, value]
      };
    });
  }

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.hero}>
        <Text style={styles.logo}>OutOfLoop</Text>
        <Text style={styles.title}>Sai do automatico no teu ritmo.</Text>
        <Text style={styles.subtitle}>
          Escolhe como queres comecar. A app adapta as primeiras missoes sem te
          empurrar para grupos.
        </Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>O que queres mexer primeiro?</Text>
        <View style={styles.grid}>
          {modes.map((mode) => (
            <OptionChip
              key={mode.value}
              label={mode.label}
              selected={preferences.primaryMode === mode.value}
              onPress={() =>
                setPreferences((current) => ({
                  ...current,
                  primaryMode: mode.value
                }))
              }
            />
          ))}
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Como preferes comecar?</Text>
        <View style={styles.grid}>
          <OptionChip
            label="Sozinho/a"
            selected={preferences.privateFirst}
            onPress={() =>
              setPreferences((current) => ({
                ...current,
                privateFirst: true
              }))
            }
          />
          <OptionChip
            label="Com pessoas"
            selected={!preferences.privateFirst}
            onPress={() =>
              setPreferences((current) => ({
                ...current,
                privateFirst: false
              }))
            }
          />
          <OptionChip
            label="Tenho filhos"
            selected={preferences.hasChildren}
            onPress={() =>
              setPreferences((current) => ({
                ...current,
                hasChildren: !current.hasChildren
              }))
            }
          />
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Intensidade</Text>
        <View style={styles.grid}>
          {intensities.map((intensity) => (
            <OptionChip
              key={intensity.value}
              label={intensity.label}
              selected={preferences.preferredIntensity === intensity.value}
              onPress={() =>
                setPreferences((current) => ({
                  ...current,
                  preferredIntensity: intensity.value
                }))
              }
            />
          ))}
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Tempo maximo por missao</Text>
        <View style={styles.grid}>
          {timeOptions.map((time) => (
            <OptionChip
              key={time.minutes}
              label={time.label}
              selected={preferences.maxMinutes === time.minutes}
              onPress={() =>
                setPreferences((current) => ({
                  ...current,
                  maxMinutes: time.minutes
                }))
              }
            />
          ))}
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Custo preferido</Text>
        <View style={styles.grid}>
          {costs.map((cost) => (
            <OptionChip
              key={cost.value}
              label={cost.label}
              selected={preferences.preferredCostTier === cost.value}
              onPress={() =>
                setPreferences((current) => ({
                  ...current,
                  preferredCostTier: cost.value
                }))
              }
            />
          ))}
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Preferencias de acessibilidade</Text>
        <Text style={styles.helper}>Privadas por defeito.</Text>
        <View style={styles.grid}>
          {accessibilityOptions.map((option) => (
            <OptionChip
              key={option}
              label={option}
              selected={preferences.accessibility.includes(option)}
              onPress={() => toggleAccessibility(option)}
            />
          ))}
        </View>
      </View>

      <View style={styles.footer}>
        <ActionButton onPress={() => onComplete(preferences)}>
          Ver a minha missao
        </ActionButton>
        <ActionButton
          variant="ghost"
          onPress={() => onComplete(defaultPreferences)}
        >
          Usar sugestoes iniciais
        </ActionButton>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  content: {
    padding: 20,
    paddingBottom: 34,
    gap: 14
  },
  hero: {
    gap: 9,
    paddingTop: 8,
    paddingBottom: 4
  },
  logo: {
    color: colors.coral,
    fontSize: 14,
    fontWeight: "900",
    letterSpacing: 0,
    textTransform: "uppercase"
  },
  title: {
    color: colors.ink,
    fontSize: 34,
    lineHeight: 38,
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
    gap: 12,
    borderWidth: 1,
    borderColor: colors.line
  },
  cardTitle: {
    color: colors.ink,
    fontSize: 18,
    fontWeight: "900",
    letterSpacing: 0
  },
  helper: {
    color: colors.inkMuted,
    fontSize: 13,
    letterSpacing: 0
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    gap: 9
  },
  footer: {
    backgroundColor: colors.background,
    gap: 8,
    paddingTop: 4
  }
});
