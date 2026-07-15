import { useState } from "react";
import {
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View
} from "react-native";

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
import type { AppUser } from "../data/user";
import { colors, radius } from "../theme/colors";

const routineFocusOptions = [
  "Sair mais de casa",
  "Conhecer melhor pessoas a minha volta",
  "Fazer planos com amigos",
  "Fazer mais coisas em familia",
  "Recuperar energia",
  "Mexer o corpo",
  "Descobrir sitios novos",
  "Ter mais aventura",
  "Criar momentos sem telemovel",
  "Reaproximar-me de alguem",
  "Fazer coisas sozinho/a",
  "Ajudar ou participar na comunidade"
];

const modeOptions: Array<{ label: string; value: MissionMode }> = [
  { label: "Social", value: "social" },
  { label: "Recuperar ritmo", value: "recomeco" },
  { label: "Aventura", value: "coragem" },
  { label: "Familia", value: "familia" },
  { label: "Saude", value: "saude" }
];

const intensities: Array<{ label: string; value: MissionIntensity }> = [
  { label: "Leve", value: "leve" },
  { label: "Real", value: "real" },
  { label: "Aventura", value: "coragem" }
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

const availabilityOptions = [
  "Manha",
  "Almoco",
  "Fim de tarde",
  "Noite",
  "Fim de semana",
  "Dias com pouca energia"
];

const energyOptions: Array<{
  label: string;
  value: AppPreferences["usualEnergy"];
}> = [
  { label: "Baixa", value: "baixa" },
  { label: "Media", value: "media" },
  { label: "Alta", value: "alta" }
];

const socialComfortOptions: Array<{
  label: string;
  value: AppPreferences["socialComfort"];
}> = [
  { label: "Sozinho/a", value: "sozinho" },
  { label: "Uma pessoa", value: "uma_pessoa" },
  { label: "Grupo pequeno", value: "grupo_pequeno" },
  { label: "Grupo", value: "grupo" }
];

const activityCompanyOptions: Array<{
  label: string;
  value: AppPreferences["activityCompanyPreference"];
}> = [
  { label: "Sozinho/a", value: "sozinho" },
  { label: "Uma pessoa", value: "uma_pessoa" },
  { label: "Grupo pequeno", value: "grupo_pequeno" },
  { label: "Grupo aberto", value: "grupo_aberto" },
  { label: "Depende", value: "depende" }
];

const soloIdeasOptions: Array<{
  label: string;
  value: AppPreferences["soloIdeasPreference"];
}> = [
  { label: "Sim, quero", value: "sim" },
  { label: "So as vezes", value: "as_vezes" },
  { label: "Prefiro com pessoas", value: "com_pessoas" }
];

const activityOptions = [
  "Caminhar",
  "Bicicleta",
  "Cafe",
  "Jantar",
  "Cinema",
  "Natureza",
  "Praia",
  "Museus",
  "Desporto leve",
  "Corrida",
  "Gym partner",
  "Viagem de moto",
  "Trilhos",
  "Padel",
  "Futebol",
  "Danca",
  "Aulas de grupo",
  "Fotografia",
  "Jogos",
  "Coisas com animais",
  "Voluntariado"
];

type EntryMode = "welcome" | "try" | "create" | "login";
type AuthMethod = "guest" | "email" | "apple" | "google";

export function OnboardingScreen({
  onComplete
}: {
  onComplete: (preferences: AppPreferences, user: AppUser) => void;
}) {
  const [preferences, setPreferences] =
    useState<AppPreferences>(defaultPreferences);
  const [entryMode, setEntryMode] = useState<EntryMode>("welcome");
  const [authMethod, setAuthMethod] = useState<AuthMethod>("guest");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [authError, setAuthError] = useState("");
  const [username, setUsername] = useState("@tu");
  const [locality, setLocality] = useState("");
  const [showName, setShowName] = useState(true);
  const [showUsername, setShowUsername] = useState(true);
  const [showLocality, setShowLocality] = useState(true);

  function complete(nextPreferences: AppPreferences) {
    const trimmedName = name.trim();
    const trimmedEmail = email.trim();
    const trimmedPassword = password.trim();
    const user: AppUser =
      authMethod !== "guest"
        ? {
            entryType: "account",
            authMethod,
            name: trimmedName || undefined,
            email: trimmedEmail || undefined,
            hasPassword: authMethod === "email" ? Boolean(trimmedPassword) : false,
            username: username.trim() || "@tu",
            locality: locality.trim() || undefined,
            visibility: {
              showPhoto: true,
              showName,
              showUsername,
              showLocality
            }
          }
        : {
            entryType: "guest",
            username: username.trim() || "@tu",
            locality: locality.trim() || undefined,
            visibility: {
              showPhoto: true,
              showName,
              showUsername,
              showLocality
            }
          };

    onComplete(nextPreferences, user);
  }

  function startEmailFlow(nextMode: "create" | "login") {
    setAuthMethod("email");
    setAuthError("");
    setEntryMode(nextMode);
  }

  function startGuestFlow() {
    setAuthMethod("guest");
    setAuthError("");
    setEntryMode("try");
  }

  function startSocialFlow(method: "apple" | "google") {
    setAuthMethod(method);
    setAuthError("");
    setEntryMode("try");
  }

  function continueWithEmail() {
    if (!email.trim()) {
      setAuthError("Escreve o email para continuar.");
      return;
    }

    if (password.trim().length < 6) {
      setAuthError("A password deve ter pelo menos 6 caracteres.");
      return;
    }

    setAuthError("");
    setEntryMode("try");
  }

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

  function toggleAvailability(value: string) {
    setPreferences((current) => {
      const exists = current.availability.includes(value);
      return {
        ...current,
        availability: exists
          ? current.availability.filter((item) => item !== value)
          : [...current.availability, value]
      };
    });
  }

  function toggleActivity(value: string) {
    setPreferences((current) => {
      const exists = current.likedActivities.includes(value);
      return {
        ...current,
        likedActivities: exists
          ? current.likedActivities.filter((item) => item !== value)
          : [...current.likedActivities, value]
      };
    });
  }

  function modeFromFocus(focus: string[]): MissionMode {
    if (
      focus.includes("Fazer mais coisas em familia") ||
      focus.includes("Criar momentos sem telemovel")
    ) {
      return "familia";
    }

    if (
      focus.includes("Recuperar energia") ||
      focus.includes("Mexer o corpo")
    ) {
      return "saude";
    }

    if (
      focus.includes("Ter mais aventura") ||
      focus.includes("Descobrir sitios novos")
    ) {
      return "coragem";
    }

    if (
      focus.includes("Reaproximar-me de alguem") ||
      focus.includes("Fazer coisas sozinho/a")
    ) {
      return "recomeco";
    }

    return "social";
  }

  function toggleRoutineFocus(value: string) {
    setPreferences((current) => {
      const exists = current.routineFocus.includes(value);
      const routineFocus = exists
        ? current.routineFocus.filter((item) => item !== value)
        : [...current.routineFocus, value];

      return {
        ...current,
        routineFocus,
        primaryMode: modeFromFocus(routineFocus)
      };
    });
  }

  return (
    <ScrollView contentContainerStyle={styles.content}>
      <View style={styles.hero}>
        <Text style={styles.logo}>OutOfLoop</Text>
        <Text style={styles.title}>Sai do automatico no teu ritmo.</Text>
        <Text style={styles.subtitle}>
          Podes experimentar primeiro. Se fizer sentido, crias conta depois.
        </Text>
      </View>

      {entryMode === "welcome" ? (
        <View style={styles.entryCard}>
          <Text style={styles.entryTitle}>Como queres entrar?</Text>
          <Text style={styles.entryText}>
            Podes comecar ja, criar conta ou entrar numa conta que ja tens.
          </Text>
          <ActionButton onPress={startGuestFlow}>
            Experimentar primeiro
          </ActionButton>
          <ActionButton variant="secondary" onPress={() => startEmailFlow("create")}>
            Criar conta
          </ActionButton>
          <ActionButton variant="ghost" onPress={() => startEmailFlow("login")}>
            Entrar
          </ActionButton>
          <View style={styles.socialRow}>
            <ActionButton
              variant="secondary"
              style={styles.socialButton}
              onPress={() => startSocialFlow("apple")}
            >
              Apple
            </ActionButton>
            <ActionButton
              variant="secondary"
              style={styles.socialButton}
              onPress={() => startSocialFlow("google")}
            >
              Google
            </ActionButton>
          </View>
        </View>
      ) : null}

      {entryMode === "create" ? (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Criar conta</Text>
          <Text style={styles.helper}>
            Usa nome, email e password. Tambem podes entrar com Apple ou Google.
          </Text>
          <TextInput
            value={name}
            onChangeText={setName}
            placeholder="Nome"
            placeholderTextColor={colors.inkMuted}
            style={styles.input}
          />
          <TextInput
            value={email}
            onChangeText={setEmail}
            placeholder="Email"
            placeholderTextColor={colors.inkMuted}
            keyboardType="email-address"
            autoCapitalize="none"
            style={styles.input}
          />
          <TextInput
            value={password}
            onChangeText={setPassword}
            placeholder="Password"
            placeholderTextColor={colors.inkMuted}
            secureTextEntry
            autoCapitalize="none"
            style={styles.input}
          />
          {authError ? <Text style={styles.errorText}>{authError}</Text> : null}
          <ActionButton onPress={continueWithEmail}>
            Continuar para as escolhas
          </ActionButton>
          <View style={styles.socialRow}>
            <ActionButton
              variant="secondary"
              style={styles.socialButton}
              onPress={() => startSocialFlow("apple")}
            >
              Apple
            </ActionButton>
            <ActionButton
              variant="secondary"
              style={styles.socialButton}
              onPress={() => startSocialFlow("google")}
            >
              Google
            </ActionButton>
          </View>
          <ActionButton variant="ghost" onPress={() => setEntryMode("welcome")}>
            Voltar
          </ActionButton>
        </View>
      ) : null}

      {entryMode === "login" ? (
        <View style={styles.card}>
          <Text style={styles.cardTitle}>Entrar</Text>
          <Text style={styles.helper}>
            Entra com email e password, ou usa Apple/Google.
          </Text>
          <TextInput
            value={email}
            onChangeText={setEmail}
            placeholder="Email"
            placeholderTextColor={colors.inkMuted}
            keyboardType="email-address"
            autoCapitalize="none"
            style={styles.input}
          />
          <TextInput
            value={password}
            onChangeText={setPassword}
            placeholder="Password"
            placeholderTextColor={colors.inkMuted}
            secureTextEntry
            autoCapitalize="none"
            style={styles.input}
          />
          {authError ? <Text style={styles.errorText}>{authError}</Text> : null}
          <ActionButton onPress={continueWithEmail}>
            Continuar para as escolhas
          </ActionButton>
          <View style={styles.socialRow}>
            <ActionButton
              variant="secondary"
              style={styles.socialButton}
              onPress={() => startSocialFlow("apple")}
            >
              Apple
            </ActionButton>
            <ActionButton
              variant="secondary"
              style={styles.socialButton}
              onPress={() => startSocialFlow("google")}
            >
              Google
            </ActionButton>
          </View>
          <ActionButton variant="ghost" onPress={() => setEntryMode("welcome")}>
            Voltar
          </ActionButton>
        </View>
      ) : null}

      {entryMode === "try" ? (
        <>
          <View style={styles.card}>
            <Text style={styles.cardTitle}>
              O que queres mexer na tua rotina?
            </Text>
            <Text style={styles.helper}>
              Escolhe tudo o que fizer sentido agora. Isto ajuda a app a
              sugerir missoes e planos mais certos para ti.
            </Text>
            <View style={styles.grid}>
              {routineFocusOptions.map((option) => (
                <OptionChip
                  key={option}
                  label={option}
                  selected={preferences.routineFocus.includes(option)}
                  onPress={() => toggleRoutineFocus(option)}
                />
              ))}
            </View>
          </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Tipo de missao principal</Text>
        <Text style={styles.helper}>
          Podes ajustar o foco principal. “Recuperar ritmo” significa voltar a
          mexer depois de uma fase parada, cansada ou isolada.
        </Text>
        <View style={styles.grid}>
          {modeOptions.map((mode) => (
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
          <OptionChip
            label="Tenho animais"
            selected={preferences.hasPets}
            onPress={() =>
              setPreferences((current) => ({
                ...current,
                hasPets: !current.hasPets
              }))
            }
          />
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Que coisas gostas de fazer?</Text>
        <Text style={styles.helper}>
          Isto ajuda a sugerir missoes e planos que parecem mais teus.
        </Text>
        <View style={styles.grid}>
          {activityOptions.map((activity) => (
            <OptionChip
              key={activity}
              label={activity}
              selected={preferences.likedActivities.includes(activity)}
              onPress={() => toggleActivity(activity)}
            />
          ))}
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Preferes fazer estas coisas como?</Text>
        <Text style={styles.helper}>
          A mesma atividade pode ser sozinho/a, a dois ou em grupo.
        </Text>
        <View style={styles.grid}>
          {activityCompanyOptions.map((option) => (
            <OptionChip
              key={option.value}
              label={option.label}
              selected={preferences.activityCompanyPreference === option.value}
              onPress={() =>
                setPreferences((current) => ({
                  ...current,
                  activityCompanyPreference: option.value
                }))
              }
            />
          ))}
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>
          Tambem queres ideias para fazer sozinho/a?
        </Text>
        <Text style={styles.helper}>
          Ajuda a app a sugerir atividades individuais quando nao queres depender
          de ninguem.
        </Text>
        <View style={styles.grid}>
          {soloIdeasOptions.map((option) => (
            <OptionChip
              key={option.value}
              label={option.label}
              selected={preferences.soloIdeasPreference === option.value}
              onPress={() =>
                setPreferences((current) => ({
                  ...current,
                  soloIdeasPreference: option.value
                }))
              }
            />
          ))}
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Quando costuma ser mais facil?</Text>
        <Text style={styles.helper}>
          Escolhe os momentos em que tens mais hipotese de aceitar uma missao ou
          plano.
        </Text>
        <View style={styles.grid}>
          {availabilityOptions.map((option) => (
            <OptionChip
              key={option}
              label={option}
              selected={preferences.availability.includes(option)}
              onPress={() => toggleAvailability(option)}
            />
          ))}
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Energia normal</Text>
        <View style={styles.grid}>
          {energyOptions.map((energy) => (
            <OptionChip
              key={energy.value}
              label={energy.label}
              selected={preferences.usualEnergy === energy.value}
              onPress={() =>
                setPreferences((current) => ({
                  ...current,
                  usualEnergy: energy.value
                }))
              }
            />
          ))}
        </View>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Com quem te sentes melhor?</Text>
        <Text style={styles.helper}>
          Isto ajuda a sugerir missoes privadas, a dois ou em grupo.
        </Text>
        <View style={styles.grid}>
          {socialComfortOptions.map((comfort) => (
            <OptionChip
              key={comfort.value}
              label={comfort.label}
              selected={preferences.socialComfort === comfort.value}
              onPress={() =>
                setPreferences((current) => ({
                  ...current,
                  socialComfort: comfort.value,
                  privateFirst: comfort.value === "sozinho"
                }))
              }
            />
          ))}
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

      <View style={styles.card}>
        <Text style={styles.cardTitle}>Como apareces aos outros?</Text>
        <Text style={styles.helper}>
          Esta informacao so faz sentido em circulos e planos. Podes alterar no
          Perfil.
        </Text>
        <TextInput
          value={username}
          onChangeText={setUsername}
          placeholder="Username"
          placeholderTextColor={colors.inkMuted}
          autoCapitalize="none"
          style={styles.input}
        />
        <TextInput
          value={locality}
          onChangeText={setLocality}
          placeholder="Localidade aproximada"
          placeholderTextColor={colors.inkMuted}
          style={styles.input}
        />
        <View style={styles.grid}>
          <OptionChip
            label="Mostrar nome"
            selected={showName}
            onPress={() => setShowName((current) => !current)}
          />
          <OptionChip
            label="Mostrar username"
            selected={showUsername}
            onPress={() => setShowUsername((current) => !current)}
          />
          <OptionChip
            label="Mostrar localidade"
            selected={showLocality}
            onPress={() => setShowLocality((current) => !current)}
          />
        </View>
      </View>

      <View style={styles.footer}>
        <ActionButton onPress={() => complete(preferences)}>
          Ver a minha missao
        </ActionButton>
        <ActionButton
          variant="ghost"
          onPress={() => complete(defaultPreferences)}
        >
          Usar sugestoes iniciais
        </ActionButton>
      </View>
        </>
      ) : null}
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
  entryCard: {
    backgroundColor: colors.green,
    borderRadius: radius.lg,
    padding: 18,
    gap: 12
  },
  entryTitle: {
    color: "#FFFFFF",
    fontSize: 26,
    lineHeight: 30,
    fontWeight: "900",
    letterSpacing: 0
  },
  entryText: {
    color: "#EEF6EF",
    fontSize: 15,
    lineHeight: 22,
    letterSpacing: 0
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
  input: {
    minHeight: 48,
    borderRadius: radius.sm,
    borderWidth: 1,
    borderColor: colors.line,
    backgroundColor: colors.surface,
    color: colors.ink,
    paddingHorizontal: 13,
    fontSize: 15,
    letterSpacing: 0
  },
  errorText: {
    color: colors.danger,
    fontSize: 13,
    lineHeight: 18,
    fontWeight: "700",
    letterSpacing: 0
  },
  socialRow: {
    flexDirection: "row",
    gap: 8
  },
  socialButton: {
    flex: 1
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
