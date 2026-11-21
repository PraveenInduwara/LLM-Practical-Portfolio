# Lab 02: LLMs in Everyday Life - ShareShelf

## Objective

Use an LLM as a product-development partner to design a practical way for students to reduce avoidable food waste, then build an interactive visual prototype.

## Assessment topic

This work develops **Group 3: The Food Waster** from Lab Sheet 2. Students may buy more food than they can eat, forget stored food, or discard leftovers because they are unsure what to do with them. Other students may be looking for affordable food. The brief asks for a product or service concept, name, key features, target user, and visual prototype/mock-up.

## Brainstorming and concept selection

Three directions were considered before implementation:

| Idea | Concept | Strength | Trade-off |
|---|---|---|---|
| LastBite Board | A campus board for time-limited, low-cost surplus meals from students and campus cafés | Connects food availability with affordability | Depends on a reliable campus community and clear pickup coordination |
| PantryPal | A shared-fridge inventory that shows what is available before students shop | Helps prevent duplicate purchases and forgotten food | Requires people sharing a fridge to keep the inventory current |
| **ShareShelf (selected)** | A student food companion for tracking “use soon” items, finding simple leftover ideas, and offering safe-to-share surplus | Addresses both forgotten food and affordable access in one place | A real service needs moderation, trust, and locally appropriate food safety rules |

ShareShelf brings all three directions together as one student food-sharing app: **PantryPal's personal food inventory**, **LastBite's community surplus board**, and **leftover prompts** that help students use what they have. A student can track food, decide to use or share an extra item, then let another student express interest in the same shared space. The browser prototype demonstrates this connected flow while clearly labeling the board as local demo data rather than a live campus service.

## Product concept

**Name:** ShareShelf  
**Tagline:** Good food deserves another chance.  
**Concept:** A student food-sharing app that combines a personal “use soon” shelf, simple leftover ideas, and a shared campus board. A student can post surplus food, and another student can claim or express interest in a listing. The prototype keeps those actions on one device; a production app would connect students through a secure shared service.

### Target users

- University students who share kitchens or live away from home and want to waste less food.
- Students who want low-cost food and can collect a clearly described surplus item.
- Student societies or campus food providers that want to direct edible surplus to people nearby.

### Key features

- Add food items with quantity and a date to use by.
- Group pantry items into fruit and vegetables, dairy and eggs, bakery, pantry staples, leftovers, and other; suggest a category from the food name and allow changing it.
- Sort and filter the shelf by items that need attention soon.
- Mark food as used or remove it from the shelf.
- Show practical leftover prompts based on the item, without claiming generated ideas are allergy-safe or food-safety advice.
- Preview sample campus-share listings with pickup notes and availability.
- Share an item directly from the personal shelf, or post extra food from the community board form.
- Claim or express interest in a listing to demonstrate the student-to-student exchange flow.
- Create named kitchen chat rooms, add friends by name, and send sample messages inside each room.
- Use a mobile-first app layout with Home, Pantry, Share, and Chats tabs.
- Keep the demonstration data in the browser using local storage.
- Responsive layout with semantic labels, keyboard-friendly controls, and visible focus states.

## Prototype

Open [`prototype/index.html`](prototype/index.html) in a modern browser. The prototype has no build step, account, or network requirement. Try the food categories, create a room and add friends by name, then send a sample message. Data is stored in that browser's local storage. [`screenshots/shareshelf_mobile_app_screens.svg`](screenshots/shareshelf_mobile_app_screens.svg) shows sample Home, Pantry, and Chats screens.

The campus listings and chats are illustrative local demo content; they do not contact friends, sync between devices, or arrange food collection. A production service would need moderation, accurate item and allergen details, clear pickup hand-offs, privacy protections, and food safety rules that apply to its location. Date prompts are reminders only; they do not determine whether food is safe to eat.

## LLM product-development process

The LLM was used to brainstorm three product directions, compare their fit to the student problem, select a concept that can be shown honestly in a browser, and review the feature list against the lab brief. The final scope focuses on tasks that can be demonstrated in the prototype. The LLM supported ideation and implementation; no claim is made that the product has reduced food waste in a real student population.

### Example prompts used

1. “Brainstorm three distinct product or service concepts for students who forget food, discard leftovers, or want affordable food. For each, include users, key features, feasibility, and a limitation.”
2. “Compare a campus surplus board, shared-fridge inventory, and student food companion. Choose one concept that can be represented as an honest browser prototype and explain what it cannot prove.”
3. “Check the selected concept against the brief: product name, concept, key features, target users, and a visual mock-up. Suggest a small accessible prototype flow.”

## Implementation and use

The prototype uses plain HTML, CSS, and JavaScript. To try it:

1. Open the prototype in a browser.
2. Add an item and its “use by” date to the pantry shelf.
3. Use the “Use soon” filter to spot items needing attention.
4. Mark an item used when it is finished, or remove it if it is no longer on the shelf.
5. Review the leftover prompts and the sample campus-share listings.
6. Use the share action to see the local demonstration state; no listing is published externally.

## Results and evidence

The deliverable is an interactive prototype rather than a static drawing. It demonstrates adding, filtering, and updating a personal food shelf alongside a separate preview of campus surplus sharing. The UI is responsive and stores demonstration state locally in the browser.

## Observations and limitations

Keeping personal inventory and community exchange in one interface makes the “use it or share it” path visible. Local storage keeps the demonstration simple, but does not synchronize between students. Demo exchange entries are fictional. The prototype has not been tested with students, and it does not verify freshness, allergies, food handling, or collection. These would need real user research and responsible operational design before launch.

## Learning outcomes

- Turn a broad everyday challenge into a defined product concept, users, and feature set.
- Use an LLM to generate and compare ideas while checking feasibility and limitations.
- Build a browser prototype with form validation, date-based reminders, filtering, local persistence, and responsive styling.
- Distinguish an illustrative mock-up from a working community service and avoid unsupported safety or impact claims.

## Files

- [`prototype/index.html`](prototype/index.html) - semantic interface structure.
- [`prototype/styles.css`](prototype/styles.css) - responsive visual design and focus states.
- [`prototype/app.js`](prototype/app.js) - categories, pantry interactions, local share previews, chat rooms, and local storage.
- [`screenshots/shareshelf_mobile_app_screens.svg`](screenshots/shareshelf_mobile_app_screens.svg) - sample Home, Pantry, and Chats screens.
