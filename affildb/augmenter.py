import json

class AffilAugmenter(object):

    def __init__(self):
        pass

        
    def _build_aff_id(self):
        aff_id = []
        for auth in self.author_data:
            author_affid_string = "; ".join([a.get("inst_id", "-") for a in auth])
            aff_id.append(author_affid_string)
        self.aff_id = aff_id

    def _build_aff_canonical(self):
        aff_canonical = []
        for auth in self.author_data:
            author_canonical_string = "; ".join([a.get("inst_canonical", "-") for a in auth])
            aff_canonical.append(author_canonical_string)
        self.aff_canonical = aff_canonical

    def _build_aff_country(self):
        aff_country = []
        for auth in self.author_data:
            author_country_string = "; ".join([a.get("inst_country", "-") for a in auth])
            aff_country.append(author_country_string)
        self.aff_country = aff_country

    def _build_aff_iso_country(self):
        aff_iso_country = []
        for auth in self.author_data:
            author_iso_country_string = "; ".join([a.get("inst_iso_country", "-") for a in auth])
            aff_iso_country.append(author_iso_country_string)
        self.aff_iso_country = aff_iso_country

    def _build_parents(self):
        self.aff_facet_hier = []
        self.aff_abbrev = []
        for auth in self.author_data:
            auth_aff_abbrev = []
            for aff in auth:
                aff_abbrev = aff.get("inst_abbreviation", "-")
                if aff_abbrev == "-":
                    auth_aff_abbrev.append(aff_abbrev)
                else:
                    aff_parents = aff.get("parent_data", [])
                    parent_abbrev = [p.get("inst_abbreviation", "-") for p in aff_parents]
                    if parent_abbrev:
                        pc_list = ["%s/%s" % (p, aff_abbrev) for p in parent_abbrev]
                        abbrev_string = "; ".join(pc_list)
                        for p in parent_abbrev:
                            facet_0 = "0/%s" % p
                            facet_1 = "1/%s/%s" % (p, aff_abbrev)
                            if facet_0 not in self.aff_facet_hier:
                                self.aff_facet_hier.append(facet_0)
                            if facet_1 not in self.aff_facet_hier:
                                self.aff_facet_hier.append(facet_1)
                    else:
                        abbrev_string = "%s/%s" % (aff_abbrev, aff_abbrev)
                        facet_0 = "0/%s" % aff_abbrev
                        facet_1 = "1/%s/%s" % (aff_abbrev, aff_abbrev)
                        if facet_0 not in self.aff_facet_hier:
                            self.aff_facet_hier.append(facet_0)
                        if facet_1 not in self.aff_facet_hier:
                            self.aff_facet_hier.append(facet_1)
                    auth_aff_abbrev.append(abbrev_string)
            self.aff_abbrev.append("; ".join(auth_aff_abbrev))
                    

    def _build_output(self):
        self.aff = self.record.get("aff", [])
        self._build_aff_canonical()
        self._build_aff_country()
        self._build_aff_iso_country()
        self._build_aff_id()
        self._build_parents()
        self.author = self.record.get("author", [])
        self.bibcode = self.record.get("bibcode", "")
        self.scixID = self.record.get("scixID", "")
        self.output = {
            "aff": self.aff,
            "aff_abbrev": self.aff_abbrev,
            "aff_country": self.aff_country,
            "aff_canonical": self.aff_canonical,
            "aff_facet_hier": self.aff_facet_hier,
            "aff_id": self.aff_id,
            "aff_iso_country": self.aff_iso_country,
            "author": self.author,
            "bibcode": self.bibcode,
            "scix_id": self.scixID
        }

    def parse(self, record, author_data):
        self.record = record
        self.author_data = author_data
        self._build_output()
        return self.output
