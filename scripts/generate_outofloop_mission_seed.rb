#!/usr/bin/env ruby

require "csv"

def sql_quote(value)
  return "null" if value.nil? || value == ""

  "'" + value.gsub("'", "''") + "'"
end

csv_path = "docs/outofloop-missions-v1.csv"
output_path = "supabase/migrations/202605190002_seed_missions.sql"
rows = CSV.read(csv_path, headers: true)

lines = []
lines << "-- Seed OutOfLoop mission library v1 (120 missions)"
lines << "insert into public.missions ("
lines << "  slug, title, description, mode, intensity, cost_tier, estimated_minutes, duration_label,"
lines << "  recommended_time_blocks, solo_enabled, pair_enabled, group_enabled, family_enabled,"
lines << "  accessibility_notes, accessible_alternative_title, accessible_alternative_description, active"
lines << ") values"

values = rows.map do |row|
  blocks = (row["recommended_time_blocks"] || "").split(",").map(&:strip).reject(&:empty?)
  block_array =
    if blocks.empty?
      "array[]::text[]"
    else
      "array[#{blocks.map { |block| sql_quote(block) }.join(", ")}]::text[]"
    end

  fields = [
    sql_quote(row["slug"]),
    sql_quote(row["title"]),
    sql_quote(row["title"]),
    sql_quote(row["mode"]),
    sql_quote(row["intensity"]),
    sql_quote(row["cost_tier"]),
    row["estimated_minutes"].to_i.to_s,
    sql_quote(row["duration_label"]),
    block_array,
    row["solo_enabled"],
    row["pair_enabled"],
    row["group_enabled"],
    row["family_enabled"],
    sql_quote(row["accessibility_notes"]),
    sql_quote(row["accessible_alternative_title"]),
    sql_quote(row["accessible_alternative_description"]),
    "true"
  ]

  "  (#{fields.join(", ")})"
end

lines << values.join(",\n")
lines << "on conflict (slug) do update set"
lines << "  title = excluded.title,"
lines << "  description = excluded.description,"
lines << "  mode = excluded.mode,"
lines << "  intensity = excluded.intensity,"
lines << "  cost_tier = excluded.cost_tier,"
lines << "  estimated_minutes = excluded.estimated_minutes,"
lines << "  duration_label = excluded.duration_label,"
lines << "  recommended_time_blocks = excluded.recommended_time_blocks,"
lines << "  solo_enabled = excluded.solo_enabled,"
lines << "  pair_enabled = excluded.pair_enabled,"
lines << "  group_enabled = excluded.group_enabled,"
lines << "  family_enabled = excluded.family_enabled,"
lines << "  accessibility_notes = excluded.accessibility_notes,"
lines << "  accessible_alternative_title = excluded.accessible_alternative_title,"
lines << "  accessible_alternative_description = excluded.accessible_alternative_description,"
lines << "  active = excluded.active;"

File.write(output_path, lines.join("\n"))
puts "Generated #{output_path} with #{rows.length} missions"
