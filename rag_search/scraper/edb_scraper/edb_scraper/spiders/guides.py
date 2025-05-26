import scrapy

from scrapy.cmdline import execute


class GuidesSpider(scrapy.Spider):
    name = "guides"
    start_urls = ["https://blog.entrepot-du-bricolage.fr/guides/le-guide-de-lisolation-thermique-et-phonique/"
                  "https://blog.entrepot-du-bricolage.fr/guides/le-guide-du-ciment-et-du-beton/",
                  "https://blog.entrepot-du-bricolage.fr/guides/outils-calculatrice/",
                  "https://blog.entrepot-du-bricolage.fr/guides/guide-entretien-maison-voiture-hiver/",
                  "https://blog.entrepot-du-bricolage.fr/guides/la-cheville-et-la-fixation/",
                  "https://blog.entrepot-du-bricolage.fr/guides/amenagement-cloison/",
                  "https://blog.entrepot-du-bricolage.fr/guides/amenagement-cuisine/",
                  "https://blog.entrepot-du-bricolage.fr/guides/guide-de-la-douche-paroi-et-receveur/",
                  "https://blog.entrepot-du-bricolage.fr/guides/la-menuiserie-interieure-et-exterieure/",
                  "https://blog.entrepot-du-bricolage.fr/guides/peinture/",
                  "https://blog.entrepot-du-bricolage.fr/guides/guide-preparation-supports/",
                  "https://blog.entrepot-du-bricolage.fr/guides/la-salle-de-bains-et-la-plomberie/",
                  "https://blog.entrepot-du-bricolage.fr/guides/la-securite-a-domicile/",
                  "https://blog.entrepot-du-bricolage.fr/guides/la-terrasse-en-bois/",
                  "https://blog.entrepot-du-bricolage.fr/guides/produits-eco-responsable-et-economie-energie/",
                  "https://blog.entrepot-du-bricolage.fr/guides/guide-carrelage/",
                  "https://blog.entrepot-du-bricolage.fr/guides/chauffage-et-confort-a-domicile/",
                  "https://blog.entrepot-du-bricolage.fr/guides/groupe-electrogene/",
                  "https://blog.entrepot-du-bricolage.fr/guides/guide-du-poele-a-bois-et-a-pellets/",
                  "https://blog.entrepot-du-bricolage.fr/guides/lamenagement-exterieur/",
                  "https://blog.entrepot-du-bricolage.fr/guides/le-guide-de-la-serrure-et-de-la-poignee-de-porte/",
                  "https://blog.entrepot-du-bricolage.fr/guides/le-guide-du-lambris-choisir-poser-et-entretenir/",
                  "https://blog.entrepot-du-bricolage.fr/guides/le-guide-du-parquet-et-du-sol-stratifie/",
                  "https://blog.entrepot-du-bricolage.fr/guides/actuellement/"]

    def parse(self, response):
        # Sélectionner tous les liens vers les guides
        guide_links = response.css('div.category__list a::attr(href)').getall()
        for link in guide_links:
            yield response.follow(link, callback=self.parse_guide)

    def parse_guide(self, response):
        title = response.css('h1::text').get()
        category = response.css('div.article__category b.category__name::text').get()
        sections = response.css('h2::text').getall()
        paragraphs = response.css('p::text').getall()
        text = ' '.join(paragraphs).strip()

        yield {
            'titre_article': title,
            'category': category,
            'titres_sections': ' | '.join(sections),
            'texte': text,
        }


if __name__ == "__main__":
    execute()
