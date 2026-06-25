#!/usr/bin/env python3
import os
import re
import shutil
import argparse
from pathlib import Path

TAGS_MAP = {
    "profile.md": "#linkedin/profile",
    "experience.md": "#linkedin/career #linkedin/experience",
    "education.md": "#linkedin/career #linkedin/education",
    "skills.md": "#linkedin/career #linkedin/skills",
    "certifications.md": "#linkedin/career #linkedin/certifications",
    "languages.md": "#linkedin/profile #linkedin/languages",
    "projects.md": "#linkedin/career #linkedin/projects",
    "recommendations.md": "#linkedin/network #linkedin/recommendations",
    "recommendations_given.md": "#linkedin/network #linkedin/recommendations",
    "connections.md": "#linkedin/network #linkedin/connections",
    "messages.md": "#linkedin/network #linkedin/messages",
    "posts.md": "#linkedin/activity #linkedin/posts",
    "comments.md": "#linkedin/activity #linkedin/comments",
    "reactions.md": "#linkedin/activity #linkedin/reactions",
    "ad_targeting.md": "#linkedin/privacy #linkedin/ads",
    "ads_clicked.md": "#linkedin/privacy #linkedin/ads",
    "lan_ads.md": "#linkedin/privacy #linkedin/ads",
    "inferences.md": "#linkedin/privacy #linkedin/inferences",
    "logins.md": "#linkedin/privacy #linkedin/activity_history",
    "search_queries.md": "#linkedin/privacy #linkedin/activity_history",
    "security_challenges.md": "#linkedin/privacy #linkedin/activity_history",
    "receipts.md": "#linkedin/payments",
    "job_applications.md": "#linkedin/jobs #linkedin/applications",
    "saved_jobs.md": "#linkedin/jobs",
    "job_preferences.md": "#linkedin/jobs",
    "saved_items.md": "#linkedin/activity",
}

def get_name_variants(full_name):
    """Generate potential matching variations for a connection name."""
    variants = {full_name}
    
    # 1. Clean emojis and special symbols
    clean = re.sub(
        r'[\u2700-\u27BF]|[\uE000-\uF8FF]|\uD83C[\uDC00-\uDFFF]|\uD83D[\uDC00-\uDFFF]|[\u2011-\u26FF]|\uD83E[\uDC00-\uDFFF]', 
        '', 
        full_name
    ).strip()
    if clean:
        variants.add(clean)
        
    # 2. Extract English / Hebrew parts from bilingual names (e.g. "Yulia Lidor יוליה לידור")
    latin_part = " ".join(re.findall(r'[a-zA-Z0-9]+(?:\s+[a-zA-Z0-9]+)*', clean)).strip()
    if latin_part:
        variants.add(latin_part)
        
    hebrew_part = " ".join(re.findall(r'[\u0590-\u05FF]+(?:\s+[\u0590-\u05FF]+)*', clean)).strip()
    if hebrew_part:
        variants.add(hebrew_part)
        
    return variants

def load_connections(connections_file):
    """Parse connections.md to extract connection names and build variation maps."""
    name_to_full_map = {}
    
    if not os.path.exists(connections_file):
        print(f"Warning: {connections_file} not found. Skipping connection resolution.")
        return name_to_full_map

    with open(connections_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('|'):
                continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 5:  # Expected: | Name | Company | Position | Connected |
                continue
            
            name = parts[1]
            if name.lower() in ('name', '') or name.startswith('---'):
                continue
                
            # Generate all matchable variations for this name
            variants = get_name_variants(name)
            for v in variants:
                name_to_full_map[v.lower()] = name

    return name_to_full_map

def find_name_in_map(comment_body, name_to_full_map):
    """Find if the start of comment_body matches any name variant in O(1) time."""
    # Normalize all whitespaces to a single standard space
    normalized = re.sub(r'[\s\xa0]+', ' ', comment_body).strip()
    words = normalized.split(' ')
    
    # Try matching prefixes from 5 words down to 1
    for length in range(min(5, len(words)), 0, -1):
        prefix = " ".join(words[:length]).strip()
        
        # Check direct lookup
        if prefix.lower() in name_to_full_map:
            return prefix, name_to_full_map[prefix.lower()]
            
        # Try checking with trailing punctuation removed
        cleaned = re.sub(r'[.,:;!?-]+$', '', prefix).strip()
        if cleaned.lower() in name_to_full_map:
            return prefix, name_to_full_map[cleaned.lower()]
            
    return None, None

def enrich_messages(content, name_to_full_map):
    """Link names in **From:** Name → **To:** Name headers."""
    def replace_header(match):
        from_name = match.group(1).strip()
        to_name = match.group(2).strip()
        
        resolved_from = name_to_full_map.get(from_name.lower(), from_name)
        resolved_to = name_to_full_map.get(to_name.lower(), to_name)
        
        from_link = f"[[{resolved_from}]]" if from_name.lower() in name_to_full_map else from_name
        to_link = f"[[{resolved_to}]]" if to_name.lower() in name_to_full_map else to_name
        
        return f"**From:** {from_link} → **To:** {to_link}"
        
    return re.sub(r"\*\*From:\*\* (.*?) → \*\*To:\*\* (.*)", replace_header, content)

def enrich_recommendations(content, name_to_full_map):
    """Link names in ## From Name and ## To Name headers."""
    def replace_from(match):
        name = match.group(1).strip()
        resolved = name_to_full_map.get(name.lower(), name)
        link = f"[[{resolved}]]" if name.lower() in name_to_full_map else name
        return f"## From {link}"

    def replace_to(match):
        name = match.group(1).strip()
        resolved = name_to_full_map.get(name.lower(), name)
        link = f"[[{resolved}]]" if name.lower() in name_to_full_map else name
        return f"## To {link}"

    content = re.sub(r"^## From (.*?)$", replace_from, content, flags=re.MULTILINE)
    content = re.sub(r"^## To (.*?)$", replace_to, content, flags=re.MULTILINE)
    return content

def enrich_comments(content, name_to_full_map):
    """Link connection names at the beginning of blockquotes (> Name)."""
    lines = content.split('\n')
    enriched_lines = []
    user_names = {"dima vishnevetsky", "dima"}
    
    for line in lines:
        if line.startswith('> '):
            comment_body = line[2:]
            matched_variant, resolved_name = find_name_in_map(comment_body, name_to_full_map)
            
            if matched_variant:
                escaped_variant = re.escape(matched_variant)
                # Convert literal spaces to match any space/non-breaking space
                space_pattern = escaped_variant.replace('\\ ', r'[\s\xa0]+')
                pattern = f"^({space_pattern})(?:\\s|\\xa0|$)"
                match = re.match(pattern, comment_body, re.IGNORECASE)
                if match:
                    end_idx = match.end(1)
                    rest = comment_body[end_idx:]
                    line = f"> [[{resolved_name}]]{rest}"
            else:
                # Check user name
                for uname in user_names:
                    pattern = f"^({re.escape(uname)})(?:\\s|\\xa0|$)"
                    match = re.match(pattern, comment_body, re.IGNORECASE)
                    if match:
                        rest = comment_body[match.end(1):]
                        line = f"> [[Dima Vishnevetsky]]{rest}"
                        break
                        
        enriched_lines.append(line)
        
    return '\n'.join(enriched_lines)

# ============================================================================
# Advanced Enrichments
# ============================================================================

def apply_file_tags(vault_dir):
    """Prepend categorizing tags to the top of vault files."""
    print("Applying Obsidian category tags...")
    for filename, tags in TAGS_MAP.items():
        filepath = Path(vault_dir) / filename
        if not filepath.exists():
            continue
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        if content.startswith('#linkedin/'):
            continue
        new_content = f"{tags}\n\n{content}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

def load_skills(skills_file):
    """Extract list of skills from skills.md."""
    if not os.path.exists(skills_file):
        return []
    with open(skills_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    skills = []
    for line in lines:
        if line.strip() and ',' in line and not line.startswith('#'):
            skills = [s.strip() for s in line.split(',') if s.strip()]
            break
            
    # Filter out extremely short terms to prevent false positives
    return [s for s in skills if len(s) > 2]

def enrich_file_with_skills(filepath, skills):
    """Link matched skills inside a file (handling word boundaries, avoiding existing links)."""
    if not filepath.exists():
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    original_content = content
    for skill in skills:
        escaped = re.escape(skill)
        # Match either an existing link [[...]] OR the skill word.
        pattern = re.compile(rf"(\[\[.*?\]\])|(\b{escaped}\b)", re.IGNORECASE)
        
        def replace(match):
            if match.group(1):
                return match.group(1)  # Return existing link as-is
            else:
                return f"[[{skill}]]"  # Wrap the skill word
                
        content = pattern.sub(replace, content)
        
    if content != original_content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def extract_entities(experience_file, education_file, companies_followed_file):
    """Extract company and school names from vault files."""
    entities = set()
    
    # 1. Experience companies
    if os.path.exists(experience_file):
        with open(experience_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('## '):
                    company = line[3:].strip()
                    if company:
                        entities.add(company)
                        
    # 2. Education schools
    if os.path.exists(education_file):
        with open(education_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('## '):
                    school = line[3:].strip()
                    if school:
                        entities.add(school)
                        
    # 3. Companies followed
    if os.path.exists(companies_followed_file):
        with open(companies_followed_file, 'r', encoding='utf-8') as f:
            for line in f:
                if line.startswith('- '):
                    comp = line[2:].strip()
                    if comp:
                        entities.add(comp)
                        
    generic_entities = {"experience", "education", "companies followed", "freelance"}
    cleaned_entities = {e for e in entities if e.lower() not in generic_entities and len(e) > 2}
    return cleaned_entities

def enrich_headers(filepath, entities):
    """Wrap headers ## Company Name into [[Company Name]] links."""
    if not filepath.exists():
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    for line in lines:
        if line.startswith('## '):
            header = line[3:].strip()
            if not header.startswith('[['):
                matched_entity = None
                for ent in entities:
                    if header.lower() == ent.lower():
                        matched_entity = ent
                        break
                if matched_entity:
                    line = f"## [[{matched_entity}]]\n"
        new_lines.append(line)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def enrich_companies_followed(filepath, entities):
    """Wrap followed company list items into [[Company Name]] links."""
    if not filepath.exists():
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    for line in lines:
        if line.startswith('- '):
            item = line[2:].strip()
            if not item.startswith('[['):
                matched_entity = None
                for ent in entities:
                    if item.lower() == ent.lower():
                        matched_entity = ent
                        break
                if matched_entity:
                    line = f"- [[{matched_entity}]]\n"
        new_lines.append(line)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def enrich_table_company_column(filepath):
    """Wrap all values in the 'Company' column of markdown tables (column index 2)."""
    if not filepath.exists():
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    for line in lines:
        if line.startswith('|'):
            parts = line.split('|')
            if len(parts) >= 5:
                company = parts[2].strip()
                # Exclude column headers, separators, and existing links
                if company and company.lower() != 'company' and not company.startswith('---') and not company.startswith('[['):
                    parts[2] = f" [[{company}]] "
                    line = "|".join(parts)
        new_lines.append(line)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def enrich_connections_table(filepath):
    """Wrap both 'Name' (column 1) and 'Company' (column 2) in connections.md table, resolving any extra pipe characters."""
    if not filepath.exists():
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    for line in lines:
        if line.startswith('|'):
            parts = [p.strip() for p in line.split('|')]
            if len(parts) >= 6:
                name = parts[1]
                connected = parts[-2]
                position = parts[-3]
                
                # Reconstruct company from any middle parts
                company_parts = parts[2:-3]
                company = " - ".join([cp.replace('[[', '').replace(']]', '').strip() for cp in company_parts])
                company = company.replace('\\\\', '\\').replace('\\', '').strip()
                
                if name.lower() != 'name' and not name.startswith('---'):
                    name_link = f"[[{name.replace('[[', '').replace(']]', '')}]]"
                    company_link = f"[[{company}]]" if company else ""
                    line = f"| {name_link} | {company_link} | {position} | {connected} |\n"
                elif name.lower() == 'name':
                    line = "| Name | Company | Position | Connected |\n"
                elif name.startswith('---'):
                    line = "|------|---------|----------|-----------|\n"
                    
        new_lines.append(line)
        
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

def enrich_recommendations_companies(filepath):
    """Wrap company names in recommendation headers: **Role** at Company | Date."""
    if not filepath.exists():
        return
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    def replace_company(match):
        role_bold = match.group(1)
        company = match.group(2).strip()
        date_part = match.group(3)
        if not company.startswith('[['):
            return f"{role_bold} at [[{company}]] |{date_part}"
        return match.group(0)
        
    content = re.sub(r"(\*\*.*?\*\*) at (.*?) \|(.*?)$", replace_company, content, flags=re.MULTILINE)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

def load_posts_mapping(posts_file):
    """Build mapping from 19-digit post/share IDs to their header dates."""
    post_id_to_header = {}
    if not os.path.exists(posts_file):
        return post_id_to_header
        
    with open(posts_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    blocks = content.split('\n---')
    for block in blocks:
        header_match = re.search(r'^##\s+(.*?)$', block, re.MULTILINE)
        if not header_match:
            continue
        header_text = header_match.group(1).strip()
        
        # Match any 19-digit number in the block (representing LinkedIn URN identifiers)
        ids = re.findall(r'\b\d{19}\b', block)
        for pid in ids:
            post_id_to_header[pid] = header_text
            
    return post_id_to_header

def enrich_comments_with_posts(comments_file, post_id_to_header):
    """Add a link to the original post inside your comment log if URN is matched."""
    if not os.path.exists(comments_file):
        return
        
    with open(comments_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    new_lines = []
    for line in lines:
        if '[View](' in line:
            ids = re.findall(r'\b\d{19}\b', line)
            matched_header = None
            for pid in ids:
                if pid in post_id_to_header:
                    matched_header = post_id_to_header[pid]
                    break
            if matched_header:
                line = line.rstrip('\r\n')
                line = f"{line} (on [[posts#{matched_header}|Post]])\n"
        new_lines.append(line)
        
    with open(comments_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)

# ============================================================================
# Statistics Report Generation
# ============================================================================

def parse_connections_stats(connections_file):
    total_connections = 0
    connections_by_year = {}
    companies_count = {}
    
    if not os.path.exists(connections_file):
        return total_connections, connections_by_year, companies_count

    with open(connections_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('|'):
                continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 5:
                continue
            name = parts[1]
            if name.lower() in ('name', '') or name.startswith('---'):
                continue
            
            total_connections += 1
            
            # Safely fetch company parts
            company_parts = parts[2:-3]
            company = " - ".join([cp.replace('[[', '').replace(']]', '').strip() for cp in company_parts])
            company = company.replace('\\\\', '\\').replace('\\', '').strip()
            
            if company:
                companies_count[company] = companies_count.get(company, 0) + 1
                
            date_str = parts[-2]
            match = re.search(r'\b(19\d\d|20\d\d)\b', date_str)
            if match:
                year = match.group(1)
                connections_by_year[year] = connections_by_year.get(year, 0) + 1
                
    return total_connections, connections_by_year, companies_count

def parse_messages_stats(messages_file):
    total_messages = 0
    sent_messages = 0
    received_messages = 0
    chat_partners = {}
    
    if not os.path.exists(messages_file):
        return total_messages, sent_messages, received_messages, chat_partners
        
    with open(messages_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pattern = re.compile(r"\*\*From:\*\* (.*?) → \*\*To:\*\* (.*)")
    matches = pattern.findall(content)
    
    for match in matches:
        from_name = match[0].replace('[[', '').replace(']]', '').strip()
        to_name = match[1].replace('[[', '').replace(']]', '').strip()
        
        total_messages += 1
        
        is_sent = "dima vishnevetsky" in from_name.lower() or "dima" == from_name.lower()
        if is_sent:
            sent_messages += 1
            partner = to_name
        else:
            received_messages += 1
            partner = from_name
            
        if partner:
            chat_partners[partner] = chat_partners.get(partner, 0) + 1
            
    return total_messages, sent_messages, received_messages, chat_partners

def count_posts(posts_file):
    if not os.path.exists(posts_file):
        return 0
    with open(posts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    headers = re.findall(r'^##\s+(.*?)$', content, re.MULTILINE)
    return len(headers)

def count_comments(comments_file):
    if not os.path.exists(comments_file):
        return 0
    count = 0
    with open(comments_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('> '):
                count += 1
    return count

def parse_reactions_stats(reactions_file):
    total_reactions = 0
    types = {}
    if not os.path.exists(reactions_file):
        return total_reactions, types
    with open(reactions_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('|'):
                continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 4:
                continue
            rtype = parts[2]
            if rtype.lower() in ('type', '') or rtype.startswith('---'):
                continue
            total_reactions += 1
            types[rtype] = types.get(rtype, 0) + 1
    return total_reactions, types

def count_recs_received(recs_file):
    if not os.path.exists(recs_file):
        return 0
    with open(recs_file, 'r', encoding='utf-8') as f:
        content = f.read()
    return len(re.findall(r'^## From', content, re.MULTILINE))

def count_recs_given(recs_given_file):
    if not os.path.exists(recs_given_file):
        return 0
    with open(recs_given_file, 'r', encoding='utf-8') as f:
        content = f.read()
    return len(re.findall(r'^## To', content, re.MULTILINE))

def count_job_applications(job_applications_file):
    if not os.path.exists(job_applications_file):
        return 0
    count = 0
    with open(job_applications_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('|'):
                continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 5:
                continue
            date = parts[1]
            if date.lower() in ('date', '') or date.startswith('---'):
                continue
            count += 1
    return count

def generate_statistics(vault_dir):
    """Scan all files inside vault_dir and generate a markdown dashboard report."""
    print("Generating profile statistics dashboard...")
    vault_path = Path(vault_dir)
    
    connections_file = vault_path / "connections.md"
    messages_file = vault_path / "messages.md"
    posts_file = vault_path / "posts.md"
    comments_file = vault_path / "comments.md"
    reactions_file = vault_path / "reactions.md"
    recs_file = vault_path / "recommendations.md"
    recs_given_file = vault_path / "recommendations_given.md"
    job_applications_file = vault_path / "job_applications.md"
    
    total_connections, connections_by_year, companies_count = parse_connections_stats(connections_file)
    total_messages, sent_messages, received_messages, chat_partners = parse_messages_stats(messages_file)
    total_posts = count_posts(posts_file)
    total_comments = count_comments(comments_file)
    total_reactions, reaction_types = parse_reactions_stats(reactions_file)
    recs_received = count_recs_received(recs_file)
    recs_given = count_recs_given(recs_given_file)
    total_jobs = count_job_applications(job_applications_file)
    
    # Growth Table
    growth_table = "| Year | New Connections |\n|------|-----------------|\n"
    for year in sorted(connections_by_year.keys(), reverse=True):
        growth_table += f"| {year} | {connections_by_year[year]} |\n"
        
    # Top Companies
    top_companies = sorted(companies_count.items(), key=lambda x: x[1], reverse=True)[:10]
    companies_table = "| Company | Connections |\n|---------|-------------|\n"
    for company, count in top_companies:
        companies_table += f"| [[{company}]] | {count} |\n"
        
    # Top Messaging Partners
    top_partners = sorted(chat_partners.items(), key=lambda x: x[1], reverse=True)[:10]
    partners_table = "| Name | Messages Exchanged |\n|------|--------------------|\n"
    for name, count in top_partners:
        partners_table += f"| [[{name}]] | {count} |\n"
        
    # Reaction Types
    reaction_table = "| Reaction Type | Count |\n|---------------|-------|\n"
    for rtype, count in sorted(reaction_types.items(), key=lambda x: x[1], reverse=True):
        reaction_table += f"| {rtype} | {count} |\n"
        
    stats_md = f"""#linkedin/statistics

# Profile Statistics & Dashboard

An overview of your LinkedIn profile and activity metrics.

## 📊 Summary Metrics

| Metric | Count | Details |
|--------|-------|---------|
| **Total Connections** | {total_connections} | 1st-degree professional network |
| **Messages Exchanged** | {total_messages} | {sent_messages} sent / {received_messages} received |
| **Posts Shared** | {total_posts} | Content shared by you |
| **Comments Made** | {total_comments} | Comments left on posts |
| **Reactions Given** | {total_reactions} | Likes/empathies/praise on content |
| **Recommendations** | {recs_received + recs_given} | {recs_received} received / {recs_given} given |
| **Job Applications** | {total_jobs} | Applications submitted via LinkedIn |

---

## 📈 Connection Growth by Year

{growth_table}

---

## 🏢 Top Companies in Network

{companies_table}

---

## 💬 Top Messaging Partners

{partners_table}

---

## ❤️ Reactions Given Breakdown

{reaction_table}
"""

    statistics_file = vault_path / "statistics.md"
    with open(statistics_file, 'w', encoding='utf-8') as f:
        f.write(stats_md)
    print("Success! Created statistics.md inside vault.")

# ============================================================================
# CRM & Company Directories Generation
# ============================================================================

def parse_messages_by_partner(messages_file):
    """Group all messages chronologically by conversation partner."""
    partner_messages = {}
    if not os.path.exists(messages_file):
        return partner_messages
        
    with open(messages_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    blocks = content.split('\n---')
    for block in blocks:
        block = block.strip()
        if not block:
            continue
            
        date_match = re.search(r'^##\s+(.*?)$', block, re.MULTILINE)
        date_str = date_match.group(1).strip() if date_match else ""
        
        header_match = re.search(r"\*\*From:\*\* (.*?) → \*\*To:\*\* (.*)", block)
        if not header_match:
            continue
            
        from_raw = header_match.group(1).strip()
        to_raw = header_match.group(2).strip()
        
        from_name = from_raw.replace('[[', '').replace(']]', '').strip()
        to_name = to_raw.replace('[[', '').replace(']]', '').strip()
        
        body = ""
        header_span = header_match.span()
        body_part = block[header_span[1]:].strip()
        if body_part:
            body = body_part
            
        is_sent = "dima vishnevetsky" in from_name.lower() or "dima" == from_name.lower()
        if is_sent:
            partner = to_name
        else:
            partner = from_name
            
        if partner:
            if partner not in partner_messages:
                partner_messages[partner] = []
            partner_messages[partner].append({
                "date": date_str,
                "from": from_raw,
                "to": to_raw,
                "body": body
            })
            
    # Reverse to restore chronological order
    for partner in partner_messages:
        partner_messages[partner].reverse()
        
    return partner_messages

def parse_connections_directory(connections_file):
    """Build employee and connection data lookups, resolving potential column shift from literal pipes."""
    people_details = {}
    company_employees = {}
    
    if not os.path.exists(connections_file):
        return people_details, company_employees
        
    with open(connections_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('|'):
                continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 5:
                continue
            name = parts[1]
            if name.lower() in ('name', '') or name.startswith('---'):
                continue
                
            clean_name = name.replace('[[', '').replace(']]', '').strip()
            connected_date = parts[-2].replace('[[', '').replace(']]', '').strip()
            position = parts[-3].replace('[[', '').replace(']]', '').strip()
            
            # Reconstruct company name safely
            company_parts = parts[2:-3]
            company = " - ".join([cp.replace('[[', '').replace(']]', '').strip() for cp in company_parts])
            company = company.replace('\\\\', '\\').replace('\\', '').strip()
            
            people_details[clean_name] = {
                "name": clean_name,
                "company": company,
                "position": position,
                "connected_date": connected_date
            }
            
            if company:
                if company not in company_employees:
                    company_employees[company] = []
                company_employees[company].append({
                    "name": clean_name,
                    "position": position
                })
                
    return people_details, company_employees

def parse_recommendations_by_person(recs_file, recs_given_file):
    """Parse recommendations file to group entries by person name."""
    recs_by_person = {}
    
    def parse_file(filepath, is_received):
        if not os.path.exists(filepath):
            return
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        blocks = content.split('\n---')
        for block in blocks:
            block = block.strip()
            if not block:
                continue
            prefix = "From" if is_received else "To"
            match = re.search(rf"^## {prefix}\s+\[\[(.*?)\]\]", block, re.MULTILINE)
            if not match:
                continue
            name = match.group(1).strip()
            
            lines = block.split('\n')
            relationship = ""
            for line in lines:
                if line.startswith('**') and ' at ' in line:
                    relationship = line.strip()
                    break
                    
            body_match = re.search(r"^>\s+(.*?)$", block, re.MULTILINE | re.DOTALL)
            body = body_match.group(1).strip() if body_match else ""
            
            if name not in recs_by_person:
                recs_by_person[name] = []
            recs_by_person[name].append({
                "type": "Received" if is_received else "Given",
                "relationship": relationship,
                "text": body
            })
            
    parse_file(recs_file, True)
    parse_file(recs_given_file, False)
    return recs_by_person

def parse_comments_by_person(comments_file):
    """Extract comment history and group by commenter name."""
    comments_by_person = {}
    if not os.path.exists(comments_file):
        return comments_by_person
        
    with open(comments_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pattern = re.compile(
        r"\*\*(.*?)\*\*\s*\n>\s*\[\[(.*?)\]\](.*)\n(?:\[View\]\((.*?)\))?",
        re.MULTILINE
    )
    matches = pattern.findall(content)
    for match in matches:
        date = match[0].strip()
        name = match[1].strip()
        text = match[2].strip()
        url = match[3].strip() if len(match) > 3 else ""
        
        if name not in comments_by_person:
            comments_by_person[name] = []
        comments_by_person[name].append({
            "date": date,
            "text": text,
            "url": url
        })
    return comments_by_person

def generate_people_pages(output_dir, people_details, partner_messages, recs_by_person, comments_by_person):
    """Create CRM-style individual profile notes inside people/."""
    people_dir = Path(output_dir) / "people"
    if people_dir.exists():
        shutil.rmtree(people_dir)
    people_dir.mkdir(parents=True, exist_ok=True)
    
    active_people = set(partner_messages.keys()) | set(recs_by_person.keys()) | set(comments_by_person.keys())
    active_people.discard("Dima Vishnevetsky")
    active_people.discard("Dima")
    
    print(f"Generating {len(active_people)} individual connection pages in people/...")
    
    for name in active_people:
        details = people_details.get(name, {
            "name": name,
            "company": "Unknown",
            "position": "Unknown",
            "connected_date": "Unknown"
        })
        
        content = f"""#linkedin/people

# {name}

## 🏢 Profile
* **Current Position:** {details['position']}
* **Company:** [[{details['company']}]]
* **Connected Date:** {details['connected_date']}
"""

        if name in recs_by_person:
            content += "\n## ⭐️ Recommendations\n"
            for rec in recs_by_person[name]:
                content += f"\n### {rec['type']}\n* **Relationship:** {rec['relationship']}\n\n> {rec['text']}\n"
                
        if name in partner_messages:
            content += "\n## 💬 Conversation History\n"
            for msg in partner_messages[name]:
                content += f"\n### {msg['date']}\n**From:** {msg['from']} → **To:** {msg['to']}\n\n{msg['body']}\n"
                
        if name in comments_by_person:
            content += "\n## 📝 Comments\n"
            for comm in comments_by_person[name]:
                content += f"\n* {comm['date']}: {comm['text']} [View Original]({comm['url']})\n"

        safe_name = re.sub(r'[\\/*?:"<>|]', "", name)
        filepath = people_dir / f"{safe_name}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

def parse_job_applications_by_company(job_applications_file):
    """Group job applications by target company."""
    apps_by_company = {}
    if not os.path.exists(job_applications_file):
        return apps_by_company
    with open(job_applications_file, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.startswith('|'):
                continue
            parts = [p.strip() for p in line.split('|')]
            if len(parts) < 5:
                continue
            date = parts[1]
            company = parts[2].replace('[[', '').replace(']]', '').strip()
            position = parts[3].strip()
            status = parts[4].strip()
            
            if date.lower() in ('date', '') or date.startswith('---'):
                continue
                
            if company:
                if company not in apps_by_company:
                    apps_by_company[company] = []
                apps_by_company[company].append({
                    "date": date,
                    "position": position,
                    "status": status
                })
    return apps_by_company

def parse_experience_by_company(experience_file):
    """Group your own work experiences by company name."""
    exp_by_company = {}
    if not os.path.exists(experience_file):
        return exp_by_company
        
    with open(experience_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    blocks = content.split('\n---')
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        match = re.search(r'^##\s+\[\[(.*?)\]\]', block, re.MULTILINE)
        if not match:
            match = re.search(r'^##\s+(.*?)$', block, re.MULTILINE)
            if not match:
                continue
        company = match.group(1).replace('[[', '').replace(']]', '').strip()
        if company:
            exp_by_company[company] = block
            
    return exp_by_company

def load_followed_companies(companies_followed_file):
    """Load followed companies list."""
    followed = set()
    if not os.path.exists(companies_followed_file):
        return followed
    with open(companies_followed_file, 'r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('- '):
                comp = line[2:].replace('[[', '').replace(']]', '').strip()
                if comp:
                    followed.add(comp)
    return followed

def generate_company_pages(output_dir, company_employees, followed_companies, apps_by_company, exp_by_company):
    """Create directory note hubs for companies inside companies/."""
    companies_dir = Path(output_dir) / "companies"
    if companies_dir.exists():
        shutil.rmtree(companies_dir)
    companies_dir.mkdir(parents=True, exist_ok=True)
    
    all_companies = (
        set(company_employees.keys()) | 
        set(followed_companies) | 
        set(apps_by_company.keys()) | 
        set(exp_by_company.keys())
    )
    
    print(f"Generating {len(all_companies)} company pages in companies/...")
    
    for company in all_companies:
        if not company or company.lower() == 'unknown':
            continue
            
        is_followed = company in followed_companies
        
        content = f"""#linkedin/company

# {company}

## 🏢 Status
* **Followed on LinkedIn:** {"Yes" if is_followed else "No"}
"""

        if company in exp_by_company:
            content += f"\n## 💼 Your Work History\n\n{exp_by_company[company]}\n"
            
        if company in apps_by_company:
            content += "\n## 📄 Your Job Applications\n\n| Date | Position | Status |\n|------|----------|--------|\n"
            for app in apps_by_company[company]:
                content += f"| {app['date']} | {app['position']} | {app['status']} |\n"
                
        connections = company_employees.get(company, [])
        if connections:
            content += f"\n## 👥 Connections working here ({len(connections)})\n\n"
            for conn in connections:
                content += f"* [[{conn['name']}]] - {conn['position']}\n"
                
        safe_company = re.sub(r'[\\/*?:"<>|]', "", company)
        filepath = companies_dir / f"{safe_company}.md"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

# ============================================================================
# Main Orchestrator
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="Enrich converted LinkedIn Markdown files with Obsidian-style links.")
    parser.add_argument(
        "-i", "--input", 
        default="../linkedin-vault", 
        help="Path to the original linkedin-vault directory containing markdown files"
    )
    parser.add_argument(
        "-o", "--output", 
        default="../linkedin-vault-obsidian", 
        help="Path where the enriched copy of the vault should be created"
    )
    args = parser.parse_args()

    input_dir = Path(args.input).resolve()
    output_dir = Path(args.output).resolve()

    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' does not exist.")
        return

    print(f"Creating enriched Obsidian vault copy...")
    print(f"Source: {input_dir}")
    print(f"Destination: {output_dir}")

    # Duplicate directory
    if output_dir.exists():
        shutil.rmtree(output_dir)
    shutil.copytree(input_dir, output_dir)

    # File paths
    connections_file = output_dir / "connections.md"
    messages_file = output_dir / "messages.md"
    recs_file = output_dir / "recommendations.md"
    recs_given_file = output_dir / "recommendations_given.md"
    comments_file = output_dir / "comments.md"
    skills_file = output_dir / "skills.md"
    experience_file = output_dir / "experience.md"
    education_file = output_dir / "education.md"
    projects_file = output_dir / "projects.md"
    companies_followed_file = output_dir / "companies_followed.md"
    job_applications_file = output_dir / "job_applications.md"
    posts_file = output_dir / "posts.md"

    # Step 1: Prepend category tags
    apply_file_tags(output_dir)

    # Step 2: Load and enrich connection names
    name_to_full_map = load_connections(connections_file)
    
    # Add User's name variants explicitly to mapping
    user_variants = get_name_variants("Dima Vishnevetsky")
    for uv in user_variants:
        name_to_full_map[uv.lower()] = "Dima Vishnevetsky"

    print(f"Loaded {len(name_to_full_map)} name mapping variants (including user name).")

    # Enrich Messages
    if messages_file.exists():
        print("Enriching messages.md...")
        with open(messages_file, 'r', encoding='utf-8') as f:
            content = f.read()
        enriched = enrich_messages(content, name_to_full_map)
        with open(messages_file, 'w', encoding='utf-8') as f:
            f.write(enriched)

    # Enrich Recommendations (names)
    for file_path in (recs_file, recs_given_file):
        if file_path.exists():
            print(f"Enriching names in {file_path.name}...")
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            enriched = enrich_recommendations(content, name_to_full_map)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(enriched)

    # Enrich Comments (names)
    if comments_file.exists():
        print("Enriching names in comments.md...")
        with open(comments_file, 'r', encoding='utf-8') as f:
            content = f.read()
        enriched = enrich_comments(content, name_to_full_map)
        with open(comments_file, 'w', encoding='utf-8') as f:
            f.write(enriched)

    # Step 3: Skill Hubs
    skills = load_skills(skills_file)
    if skills:
        print(f"Loaded {len(skills)} skills. Resolving skill mentions in experience.md & projects.md...")
        sorted_skills = sorted(skills, key=len, reverse=True)
        enrich_file_with_skills(experience_file, sorted_skills)
        enrich_file_with_skills(projects_file, sorted_skills)

    # Step 4: Company & School Clusters (Stage 1: Link in raw logs)
    entities = extract_entities(experience_file, education_file, companies_followed_file)
    if entities:
        print(f"Loaded {len(entities)} company/school entities. Clustering files...")
        enrich_headers(experience_file, entities)
        enrich_headers(education_file, entities)
        enrich_companies_followed(companies_followed_file, entities)
        enrich_table_company_column(job_applications_file)
        enrich_recommendations_companies(recs_file)
        enrich_recommendations_companies(recs_given_file)

    # Step 5: Comment-to-Post Linking
    post_id_to_header = load_posts_mapping(posts_file)
    if post_id_to_header:
        print(f"Mapped {len(post_id_to_header)} post IDs. Linking comments to posts...")
        enrich_comments_with_posts(comments_file, post_id_to_header)

    # Step 6: Generate CRM directories (people/ and companies/)
    partner_messages = parse_messages_by_partner(messages_file)
    people_details, company_employees = parse_connections_directory(connections_file)
    recs_by_person = parse_recommendations_by_person(recs_file, recs_given_file)
    comments_by_person = parse_comments_by_person(comments_file)
    followed_companies = load_followed_companies(companies_followed_file)
    apps_by_company = parse_job_applications_by_company(job_applications_file)
    exp_by_company = parse_experience_by_company(experience_file)

    # Generate individual directories
    generate_people_pages(output_dir, people_details, partner_messages, recs_by_person, comments_by_person)
    generate_company_pages(output_dir, company_employees, followed_companies, apps_by_company, exp_by_company)

    # Step 7: Final table enrichments (enrich both Name and Company columns in connections.md)
    enrich_connections_table(connections_file)

    # Step 8: Generate Dashboard Report
    generate_statistics(output_dir)

    print(f"\nSuccess! Enriched vault is ready at: {output_dir}")

if __name__ == "__main__":
    main()
