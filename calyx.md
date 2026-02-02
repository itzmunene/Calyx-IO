# Calyx - Design Specification Document
**Version 1.0 | iOS Mobile Application**

---

## 1. Product Overview

### 1.1 Product Name
**Calyx** - Your Personal Flower Discovery & Documentation App

### 1.2 Product Vision
Calyx is a mobile application that empowers users to discover, identify, and curate their own digital herbarium of flowers. Whether you're a gardening enthusiast, botanist, or nature lover, Calyx makes it easy to search for flowers, save your favorites, and build a personalized catalog of discoveries.

### 1.3 Target Platform
- **Primary Platform**: iOS (iPhone)
- **Minimum iOS Version**: iOS 15.0+
- **Device Support**: iPhone (optimized for iPhone 12 and newer)
- **Future Platform**: Android (Phase 2)

### 1.4 Core Value Proposition
- Quick and accurate flower search functionality
- Personal documentation and cataloging system
- Secure user authentication
- Search history tracking
- Beautiful, nature-inspired interface

---

## 2. User Personas

### Primary Persona: The Garden Enthusiast
- **Age**: 28-55
- **Goals**: Document flowers in their garden, learn about new species, plan future plantings
- **Pain Points**: Forgetting flower names, losing track of plants they've seen, difficulty organizing plant information

### Secondary Persona: The Nature Explorer
- **Age**: 22-45
- **Goals**: Identify flowers on hikes, build a collection of discovered species
- **Pain Points**: Can't identify flowers in the wild, no way to remember discoveries

---

## 3. Feature Specifications

### 3.1 User Authentication

#### Sign Up
- **Required Fields**:
  - Email address
  - Password (minimum 8 characters, must include uppercase, lowercase, and number)
  - Display name
- **Optional Fields**:
  - Profile photo
- **Validation**:
  - Email format validation
  - Password strength indicator
  - Duplicate email checking
- **Success Flow**: Redirect to onboarding/home screen

#### Sign In
- **Required Fields**:
  - Email address
  - Password
- **Features**:
  - "Remember Me" toggle
  - "Forgot Password" link
  - Biometric authentication (Face ID/Touch ID) after initial login
- **Error Handling**:
  - Clear error messages for incorrect credentials
  - Account lockout after 5 failed attempts (temporary, 15 minutes)

#### Password Reset
- Email-based password reset flow
- Secure token generation
- Password reset link expires after 1 hour

### 3.2 Flower Search

#### Search Interface
- **Search Input**:
  - Prominent search bar on home screen
  - Auto-complete suggestions as user types
  - Search by common name or scientific name
  - Voice search capability (optional Phase 2)

#### Search Methods
1. **Text Search**: Direct search by flower name
2. **Filter Search**: 
   - By color
   - By bloom season
   - By region/climate
   - By plant type (annual, perennial, etc.)

#### Search Results
- **Display Format**:
  - Grid view (default) or List view toggle
  - Each result shows:
    - Flower thumbnail image
    - Common name
    - Scientific name (italic, smaller font)
    - Quick "Save" button icon
- **Sorting Options**:
  - Relevance (default)
  - Alphabetical (A-Z)
  - Most popular
- **Pagination**: Load 20 results at a time with infinite scroll

#### Flower Detail View
When user taps on a search result:
- **Hero image**: Large, high-quality flower photo
- **Information sections**:
  - Common name & scientific name
  - Family classification
  - Description (origin, characteristics)
  - Growing conditions (light, water, soil)
  - Bloom time
  - Height/spread
  - Hardiness zones
  - Care tips
- **Action buttons**:
  - Save to Saved Flowers
  - Share (iOS share sheet)
  - Add notes (personal documentation)

### 3.3 Search History (Catalog Tab)

#### Features
- **Automatic tracking**: All searches automatically saved with timestamp
- **Display**:
  - Chronological list (newest first)
  - Group by date (Today, Yesterday, This Week, Earlier)
  - Each entry shows:
    - Flower thumbnail
    - Flower name
    - Search date/time
    - Quick access to flower details
- **Management**:
  - Swipe to delete individual searches
  - "Clear All" option (with confirmation dialog)
  - Search within history

#### Data Retention
- History stored locally and synced to user account
- No automatic deletion (user-controlled)

### 3.4 Saved Flowers Tab

#### Features
- **Personal Collection**: User-curated list of saved flowers
- **Display Options**:
  - Grid view (2 columns with images)
  - List view (with thumbnail + name)
- **Organization**:
  - Create custom collections/folders (e.g., "My Garden", "Wish List", "Spring Blooms")
  - Drag and drop to reorder
  - Bulk selection for moving to collections
- **Each Saved Flower Includes**:
  - All original flower information
  - Personal notes field (editable)
  - Date saved
  - Optional: Photo upload capability for user's own photos of the flower
  - Tags (custom user tags)

#### Actions
- Remove from saved
- Share individual flower or entire collection
- Export collection as PDF

### 3.5 User Profile

#### Profile Information
- Display name
- Email (displayed, not editable in-app)
- Profile photo
- Member since date
- Statistics:
  - Total flowers searched
  - Total saved flowers
  - Collections created

#### Settings
- Account settings
  - Change password
  - Email preferences
  - Delete account
- App settings
  - Notifications toggle
  - Default view preference (grid/list)
  - Measurement units (metric/imperial)
- Privacy
  - Data export
  - Clear cache
- About
  - App version
  - Terms of service
  - Privacy policy
  - Help & support

---

## 4. Information Architecture

### 4.1 Navigation Structure

**Tab Bar Navigation (Bottom)**:
1. **Home** (Search icon)
   - Search interface
   - Featured flowers section
   - Quick filter chips

2. **Catalog** (History icon)
   - Search history
   - Chronological list

3. **Saved** (Bookmark/Heart icon)
   - Saved flowers
   - Collections

4. **Profile** (User icon)
   - User info
   - Settings
   - Stats

### 4.2 Screen Hierarchy

```
├── Authentication
│   ├── Welcome/Landing
│   ├── Sign In
│   ├── Sign Up
│   └── Password Reset
│
├── Home (Search)
│   ├── Search Results
│   └── Flower Detail
│       ├── Save Confirmation
│       └── Add Notes
│
├── Catalog (History)
│   └── Flower Detail (from history)
│
├── Saved Flowers
│   ├── Collections View
│   ├── Collection Detail
│   └── Flower Detail (from saved)
│       └── Edit Notes
│
└── Profile
    ├── Edit Profile
    ├── Settings
    ├── Help & Support
    └── About
```

---

## 5. User Flows

### 5.1 First-Time User Flow
1. Download app from App Store
2. Open app → See welcome screen with app benefits
3. Tap "Get Started" → Sign Up screen
4. Create account (email, password, name)
5. Optional: Brief onboarding tutorial (swipeable cards)
6. Land on Home screen (Search)

### 5.2 Search & Save Flow
1. User on Home screen
2. Tap search bar → Keyboard appears
3. Type flower name (e.g., "rose")
4. See auto-complete suggestions
5. Tap suggestion or press search
6. View search results (grid of flowers)
7. Tap a flower → Flower detail view
8. Read information
9. Tap "Save" button → Saved confirmation + option to add to collection
10. Flower added to Saved tab
11. Search automatically added to Catalog tab

### 5.3 Browse Saved Flowers Flow
1. User taps Saved tab
2. See grid of saved flowers
3. Option to filter by collection
4. Tap a flower → View details with personal notes
5. Edit notes if desired
6. Return to Saved list

---

## 6. Technical Specifications

### 6.1 Technology Stack Recommendations

#### Frontend
- **Framework**: SwiftUI (modern, declarative UI)
- **Minimum iOS**: 15.0
- **Languages**: Swift 5.5+

#### Backend
- **API**: RESTful API or GraphQL
- **Authentication**: JWT tokens + OAuth 2.0
- **Database**: 
  - User data: PostgreSQL or MongoDB
  - Flower database: PostgreSQL with full-text search
- **Cloud Storage**: AWS S3 or Cloudinary for images
- **Hosting**: AWS, Google Cloud, or Firebase

#### Third-Party Services
- **Authentication**: Firebase Auth or Auth0 (biometric support)
- **Analytics**: Firebase Analytics or Mixpanel
- **Crash Reporting**: Firebase Crashlytics or Sentry
- **Push Notifications**: Firebase Cloud Messaging or APNs

### 6.2 Data Models

#### User Model
```
User {
  id: UUID
  email: String (unique, indexed)
  passwordHash: String
  displayName: String
  profilePhotoURL: String?
  createdAt: DateTime
  lastLoginAt: DateTime
  preferences: UserPreferences
}

UserPreferences {
  defaultView: String (grid/list)
  measurementUnit: String (metric/imperial)
  notificationsEnabled: Boolean
}
```

#### Flower Model
```
Flower {
  id: UUID
  commonName: String
  scientificName: String
  family: String
  description: String
  imageURLs: [String]
  growingConditions: GrowingConditions
  bloomSeason: [String]
  hardiness: String
  height: String
  spread: String
  careTips: String
  tags: [String]
}

GrowingConditions {
  light: String (full sun, partial shade, shade)
  water: String (low, medium, high)
  soilType: String
  pH: String
}
```

#### SavedFlower Model
```
SavedFlower {
  id: UUID
  userId: UUID (foreign key)
  flowerId: UUID (foreign key)
  savedAt: DateTime
  collectionId: UUID? (foreign key)
  personalNotes: String?
  userPhotos: [String]?
  tags: [String]?
}
```

#### SearchHistory Model
```
SearchHistory {
  id: UUID
  userId: UUID (foreign key)
  flowerId: UUID (foreign key)
  searchQuery: String
  searchedAt: DateTime
}
```

#### Collection Model
```
Collection {
  id: UUID
  userId: UUID (foreign key)
  name: String
  description: String?
  createdAt: DateTime
  flowerCount: Integer (computed)
}
```

### 6.3 API Endpoints

#### Authentication
- `POST /auth/signup` - Create new user account
- `POST /auth/login` - User login
- `POST /auth/logout` - User logout
- `POST /auth/refresh` - Refresh JWT token
- `POST /auth/forgot-password` - Request password reset
- `POST /auth/reset-password` - Reset password with token

#### Flowers
- `GET /flowers/search?query={text}&filters={}` - Search flowers
- `GET /flowers/:id` - Get flower details
- `GET /flowers/featured` - Get featured flowers (home screen)

#### Saved Flowers
- `POST /saved` - Save a flower
- `GET /saved` - Get all saved flowers for user
- `PUT /saved/:id` - Update saved flower (notes, tags)
- `DELETE /saved/:id` - Remove saved flower
- `GET /saved/collections/:collectionId` - Get flowers in collection

#### Collections
- `POST /collections` - Create new collection
- `GET /collections` - Get all user collections
- `PUT /collections/:id` - Update collection
- `DELETE /collections/:id` - Delete collection

#### Search History
- `GET /history` - Get search history
- `DELETE /history/:id` - Delete history item
- `DELETE /history/clear` - Clear all history

#### User Profile
- `GET /user/profile` - Get user profile
- `PUT /user/profile` - Update profile
- `PUT /user/password` - Change password
- `DELETE /user/account` - Delete account
- `GET /user/stats` - Get user statistics

### 6.4 Performance Requirements
- App launch time: < 2 seconds (cold start)
- Search results: < 1 second response time
- Image loading: Progressive loading with placeholders
- Offline capability: Cache recent searches and saved flowers
- Data sync: Background sync when online

### 6.5 Security Requirements
- HTTPS for all API communications
- Password hashing: bcrypt with salt
- JWT token expiration: 24 hours
- Refresh token expiration: 30 days
- Biometric authentication storage in iOS Keychain
- Input validation and sanitization
- Rate limiting on API endpoints
- GDPR compliance for data export/deletion

---

## 7. UI/UX Design Guidelines

### 7.1 Design Philosophy
Calyx should feel organic, fresh, and botanical while maintaining modern iOS design standards. The interface should be clean, allowing the beautiful flower imagery to take center stage.

### 7.2 Color Palette

**Primary Colors**:
- **Botanical Green**: #2D5016 (primary actions, accents)
- **Sage Green**: #8FA888 (secondary elements)
- **Cream**: #F5F1E8 (backgrounds)
- **Earth Brown**: #6B4423 (text, grounding elements)

**Accent Colors**:
- **Petal Pink**: #E8B4B8 (saved/favorited items)
- **Sky Blue**: #A8C5DA (informational elements)
- **Soft Yellow**: #F4E4C1 (highlights, warnings)

**Neutral Colors**:
- **White**: #FFFFFF
- **Light Gray**: #F0F0F0 (card backgrounds)
- **Medium Gray**: #C4C4C4 (borders, dividers)
- **Dark Gray**: #4A4A4A (body text)
- **Black**: #1A1A1A (headings)

### 7.3 Typography

**Primary Font**: SF Pro (iOS system font)
- **Display/Headings**: SF Pro Display
  - H1: 28pt, Bold
  - H2: 22pt, Semibold
  - H3: 18pt, Semibold
- **Body Text**: SF Pro Text
  - Body: 16pt, Regular
  - Small: 14pt, Regular
  - Caption: 12pt, Regular
- **Scientific Names**: SF Pro Text, Italic, 14pt

### 7.4 Iconography
- Use SF Symbols for consistency with iOS
- Custom botanical line icons for unique features
- Icon style: Rounded, organic shapes
- Icon colors: Align with color palette

### 7.5 Spacing & Layout
- **Base unit**: 8pt grid system
- **Screen margins**: 16pt (left/right)
- **Card padding**: 16pt
- **Element spacing**: 8pt, 16pt, 24pt, 32pt
- **Corner radius**: 
  - Cards: 12pt
  - Buttons: 8pt
  - Input fields: 8pt

### 7.6 Key Screen Designs

#### Welcome/Landing Screen
- Full-screen botanical background (subtle, not overwhelming)
- App logo centered
- Tagline: "Discover. Save. Grow Your Flower Knowledge"
- Two primary buttons: "Sign In" and "Create Account"
- Minimalist design

#### Home (Search) Screen
- Large search bar at top (rounded, with search icon)
- Below search: Quick filter chips (By Color, By Season, By Type)
- "Featured Flowers" section with horizontal scrolling cards
- Each card: Beautiful flower image, name overlay
- Bottom: Tab bar navigation

#### Search Results Screen
- Search query displayed at top with edit capability
- View toggle (grid/list) in top right
- Filter button in top right
- Results in 2-column grid:
  - Square image (aspect ratio 1:1)
  - Common name below image
  - Small heart icon in corner for quick save
- Pull to refresh

#### Flower Detail Screen
- Hero image at top (full width, 60% screen height)
- Back button (top left)
- Share button (top right)
- Scroll for information:
  - Common name (large, bold)
  - Scientific name (italic, below)
  - Tabbed sections: Overview, Care, Details
  - Information presented in clean, readable format
- Sticky footer: "Save to Collection" button (prominent)

#### Saved Flowers Screen
- Header: "My Saved Flowers" with count
- Sort/filter options (top right)
- Grid view of saved flowers (2 columns)
- Each card: Image, name, date saved
- Tap to view details
- Long press for quick actions (remove, move to collection)

#### Catalog (History) Screen
- Header: "Search History"
- Grouped by date sections (Today, Yesterday, etc.)
- List view:
  - Small thumbnail (left)
  - Flower name
  - Search timestamp
  - Chevron (right) to view details
- Swipe left to delete
- "Clear All" button at bottom

### 7.7 Animations & Interactions
- **Transitions**: Smooth, natural (0.3s duration)
- **Button press**: Subtle scale down (0.95)
- **Pull to refresh**: Organic loading indicator (flower blooming animation)
- **Save action**: Heart icon animation (scale + color change)
- **Image loading**: Fade-in with blur effect
- **Tab switching**: Crossfade transition

### 7.8 Component Library

**Buttons**:
- Primary: Filled, botanical green background, white text
- Secondary: Outlined, botanical green border, green text
- Tertiary: Text only, botanical green text
- Height: 48pt (adequate touch target)

**Input Fields**:
- Border: 1pt medium gray
- Focus state: 2pt botanical green border
- Placeholder: Medium gray text
- Error state: Red border with error message below

**Cards**:
- Background: White or light gray
- Border: 1pt light gray or none (use shadow)
- Shadow: Subtle (0pt 2pt 8pt rgba(0,0,0,0.1))
- Padding: 16pt

**Search Bar**:
- Background: Light gray
- Height: 44pt
- Rounded corners: 22pt (fully rounded)
- Search icon: Left side
- Clear button: Right side (when text entered)

---

## 8. Accessibility

### 8.1 Requirements
- **VoiceOver Support**: All elements properly labeled
- **Dynamic Type**: Support for user font size preferences
- **Color Contrast**: WCAG AA compliance (4.5:1 for text)
- **Touch Targets**: Minimum 44x44pt for all interactive elements
- **Alternative Text**: All images have descriptive alt text
- **Keyboard Navigation**: Full app usable with external keyboard
- **Reduced Motion**: Respect user's reduced motion preference

---

## 9. Onboarding Experience

### 9.1 First-Time User Tutorial (Optional Skip)
**Screen 1**: "Discover Thousands of Flowers"
- Visual: Beautiful flower grid
- Text: Search by name, color, or season

**Screen 2**: "Build Your Personal Collection"
- Visual: Saved flowers interface
- Text: Save favorites and organize into collections

**Screen 3**: "Track Your Journey"
- Visual: History/catalog view
- Text: Automatically keep track of every flower you explore

**Screen 4**: "Ready to Start?"
- Call to action button: "Explore Flowers"

---

## 10. Future Enhancements (Phase 2+)

### 10.1 Potential Features
- **Image Recognition**: Take a photo to identify flowers
- **Social Features**: Share collections with friends, follow other users
- **Garden Planner**: Visual garden layout tool
- **Reminders**: Care reminders for saved flowers
- **Offline Mode**: Full offline flower database
- **AR Preview**: See how flowers look in your space
- **Community**: User-submitted photos and reviews
- **Bloom Tracking**: Track when saved flowers bloom
- **Shopping Integration**: Links to purchase seeds/plants
- **Widget**: iOS home screen widget with flower of the day

---

## 11. Success Metrics

### 11.1 Key Performance Indicators (KPIs)
- **User Acquisition**: 
  - New sign-ups per month
  - App Store conversion rate
- **Engagement**:
  - Daily active users (DAU)
  - Monthly active users (MAU)
  - Average session duration
  - Searches per user per session
- **Retention**:
  - Day 1, 7, 30 retention rates
  - Churn rate
- **Feature Usage**:
  - % of users with saved flowers
  - Average number of saved flowers per user
  - Collection creation rate
  - Search history usage

### 11.2 User Satisfaction
- App Store rating goal: 4.5+ stars
- In-app feedback/rating prompts
- User surveys (quarterly)

---

## 12. Launch Strategy

### 12.1 MVP (Minimum Viable Product) - Phase 1
**Must-Have Features for Launch**:
- User authentication (sign up, sign in)
- Flower search functionality
- Search history (catalog)
- Save flowers
- Basic flower detail view
- User profile with settings

**Timeline**: 3-4 months development

### 12.2 Beta Testing
- Internal testing: 2 weeks
- Closed beta (TestFlight): 50-100 users, 3-4 weeks
- Collect feedback and iterate
- Bug fixes and performance optimization

### 12.3 App Store Preparation
- App Store listing copy
- Screenshots and preview video
- Keywords optimization for ASO (App Store Optimization)
- Privacy policy and terms of service

---

## 13. Maintenance & Support

### 13.1 Post-Launch
- Monitor crash reports and fix critical bugs (within 24-48 hours)
- Weekly analytics review
- Monthly feature updates
- Quarterly major updates
- User support email: support@calyxapp.com

### 13.2 Content Updates
- Flower database updates: Monthly new additions
- Seasonal featured flowers
- Content accuracy reviews

---

## 14. Legal & Compliance

### 14.1 Required Documentation
- Privacy Policy (GDPR, CCPA compliant)
- Terms of Service
- Data retention policy
- Cookie policy (if web version exists)

### 14.2 Data Protection
- User consent for data collection
- Right to export data
- Right to delete account and all data
- Transparent data usage policies

### 14.3 Content Licensing
- Ensure all flower images are properly licensed
- Attribution for botanical information sources
- Copyright compliance

---

## 15. Appendix

### 15.1 Glossary
- **Hardiness Zone**: Geographic areas defined by climate conditions
- **Perennial**: Plant that lives for more than two years
- **Annual**: Plant that completes its life cycle in one growing season
- **Calyx**: The sepals of a flower, typically forming a protective layer (app namesake)

### 15.2 References
- iOS Human Interface Guidelines
- USDA Plant Database
- Royal Horticultural Society
- Material Design (for Android future development)

### 15.3 Contact
- **Project Owner**: [Your Name]
- **Project Start Date**: February 2026
- **Document Version**: 1.0
- **Last Updated**: February 2, 2026

---

**End of Design Specification**
