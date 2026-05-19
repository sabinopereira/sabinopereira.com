import { ReactNode } from "react";
import {
  Pressable,
  StyleSheet,
  Text,
  ViewStyle
} from "react-native";

import { colors, radius } from "../theme/colors";

type Variant = "primary" | "secondary" | "ghost";

export function ActionButton({
  children,
  onPress,
  variant = "primary",
  style
}: {
  children: ReactNode;
  onPress?: () => void;
  variant?: Variant;
  style?: ViewStyle;
}) {
  return (
    <Pressable
      accessibilityRole="button"
      onPress={onPress}
      style={({ pressed }) => [
        styles.base,
        styles[variant],
        pressed && styles.pressed,
        style
      ]}
    >
      <Text style={[styles.text, styles[`${variant}Text`]]}>{children}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: {
    minHeight: 46,
    alignItems: "center",
    justifyContent: "center",
    borderRadius: radius.sm,
    paddingHorizontal: 16
  },
  primary: {
    backgroundColor: colors.green
  },
  secondary: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.line
  },
  ghost: {
    backgroundColor: "transparent"
  },
  pressed: {
    opacity: 0.78
  },
  text: {
    fontSize: 15,
    fontWeight: "800",
    letterSpacing: 0
  },
  primaryText: {
    color: "#FFFFFF"
  },
  secondaryText: {
    color: colors.ink
  },
  ghostText: {
    color: colors.inkMuted
  }
});
